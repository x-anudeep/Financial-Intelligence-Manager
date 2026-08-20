from io import BytesIO
from datetime import datetime
import os
from pathlib import Path
import re

import pandas as pd
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.financial_engine.calculations import enrich_periods
from app.financial_engine.labels import normalize_label
from app.models.financial import Company, FinancialMetric, FinancialPeriod


ARCHIVE_METRIC_MAP: dict[str, tuple[str, float]] = {
    "Current Price": ("current_price", 1),
    "Market Capitalization": ("market_cap", 1),
    "Sales": ("revenue", 1),
    "Operating profit": ("ebitda", 1),
    "Profit after tax": ("net_income", 1),
    "EPS": ("eps", 1),
    "Return on capital employed": ("roce", 0.01),
    "OPM": ("ebitda_margin", 0.01),
    "NPM last year": ("net_margin", 0.01),
    "Sales growth 3Years": ("sales_growth_3y", 0.01),
    "Sales growth 5Years": ("sales_growth_5y", 0.01),
    "Profit growth 3Years": ("profit_growth_3y", 0.01),
    "Profit growth 5Years": ("profit_growth_5y", 0.01),
    "Debt": ("total_debt", 1),
    "Total Assets": ("total_assets", 1),
    "Current assets": ("current_assets", 1),
    "Current liabilities": ("current_liabilities", 1),
    "Inventory": ("inventory", 1),
    "Trade receivables": ("accounts_receivable", 1),
    "Trade Payables": ("accounts_payable", 1),
    "Cash Equivalents": ("cash", 1),
    "Working capital": ("working_capital", 1),
    "Cash from operations last year": ("operating_cash_flow", 1),
    "Free cash flow last year": ("free_cash_flow", 1),
    "Price to Earning": ("pe_ratio", 1),
    "Dividend yield": ("dividend_yield", 0.01),
    "Price to book value": ("price_to_book", 1),
    "Return on assets": ("return_on_assets", 0.01),
    "Debt to equity": ("debt_to_equity", 1),
    "Return on equity": ("return_on_equity", 0.01),
    "Promoter holding": ("promoter_holding", 0.01),
    "Pledged percentage": ("pledged_percentage", 0.01),
    "Industry PE": ("industry_pe", 1),
    "Book value": ("book_value", 1),
    "Piotroski score": ("piotroski_score", 1),
    "FII holding": ("fii_holding", 0.01),
    "DII holding": ("dii_holding", 0.01),
    "Price to Sales": ("price_to_sales", 1),
    "Price to Free Cash Flow": ("price_to_free_cash_flow", 1),
    "EVEBITDA": ("ev_ebitda", 1),
    "PEG Ratio": ("peg_ratio", 1),
    "QoQ Profits": ("qoq_profit_growth", 0.01),
    "QoQ Sales": ("qoq_sales_growth", 0.01),
    "Intrinsic Value": ("intrinsic_value", 1),
    "Altman Z Score": ("altman_z_score", 1),
    "Return over 1day": ("return_1d", 0.01),
    "Return over 1week": ("return_1w", 0.01),
    "Return over 1month": ("return_1m", 0.01),
    "Return over 3months": ("return_3m", 0.01),
    "Return over 6months": ("return_6m", 0.01),
    "Return over 1year": ("return_1y", 0.01),
    "Return over 3years": ("return_3y", 0.01),
    "Return over 5years": ("return_5y", 0.01),
    "Volume": ("volume", 1),
    "Volume 1month average": ("volume_1m_avg", 1),
    "High price": ("high_price", 1),
    "Low price": ("low_price", 1),
    "High price all time": ("all_time_high", 1),
    "Low price all time": ("all_time_low", 1),
    "DMA 50": ("dma_50", 1),
    "DMA 200": ("dma_200", 1),
    "RSI": ("rsi", 1),
    "MACD": ("macd", 1),
    "MACD Signal": ("macd_signal", 1),
    "t_1_price": ("previous_close", 1),
}


def archive_data_dir() -> Path:
    configured = os.getenv("ARCHIVE_DATA_DIR")
    if configured:
        candidate = Path(configured)
        if candidate.exists() and list(candidate.glob("*.csv")):
            return candidate
    candidates = [
        Path.cwd() / "data" / "archive-2",
        Path("/Users/anudeep/Downloads/archive-2/dataset/dataset"),
        Path("/Users/anudeep/Downloads/archive-2/dataset"),
        Path("/Users/anudeep/Downloads/archive-2"),
    ]
    for candidate in candidates:
        if candidate.exists() and list(candidate.glob("*.csv")):
            return candidate
    raise ValueError("Archive CSVs were not found. Set ARCHIVE_DATA_DIR or place them in data/archive-2.")


def _archive_metric_name(label: str) -> tuple[str, float] | None:
    if label in ARCHIVE_METRIC_MAP:
        return ARCHIVE_METRIC_MAP[label]
    key = re.sub(r"[^a-z0-9]+", "_", label.strip().lower()).strip("_")
    return (key, 1) if key in {"current_ratio", "interest_coverage", "leverage", "croic"} else None


def _numeric(value: object, scale: float = 1) -> float | None:
    parsed = pd.to_numeric(value, errors="coerce")
    return None if pd.isna(parsed) else float(parsed) * scale


def _snake_name(label: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", str(label).strip().lower()).strip("_")


def _first_column(columns: dict[str, str], names: tuple[str, ...]) -> str | None:
    for name in names:
        if name in columns:
            return columns[name]
    return None


def _period_parts(row: pd.Series, lower_columns: dict[str, str]) -> tuple[str, int]:
    year_col = _first_column(lower_columns, ("fiscal_year", "fiscal year", "year", "fy"))
    period_col = _first_column(lower_columns, ("period", "quarter", "date", "result_date", "last result date", "last annual result date"))
    fiscal_year: int | None = None
    if year_col:
        parsed_year = pd.to_numeric(row[year_col], errors="coerce")
        if pd.notna(parsed_year):
            fiscal_year = int(parsed_year)
    if fiscal_year is None and period_col:
        parsed_date = pd.to_datetime(row[period_col], errors="coerce")
        if pd.notna(parsed_date):
            fiscal_year = int(parsed_date.year)
    if fiscal_year is None:
        fiscal_year = datetime.utcnow().year

    if period_col and pd.notna(row[period_col]):
        period = str(row[period_col]).strip()
    else:
        period = f"FY{fiscal_year}" if year_col else "Snapshot"
    return period, fiscal_year


def _metric_mapping(label: str) -> tuple[str, float] | None:
    normalized = normalize_label(label)
    if normalized:
        return normalized, 1
    archive_metric = _archive_metric_name(label)
    if archive_metric:
        return archive_metric
    snake = _snake_name(label)
    if not snake:
        return None
    identifier_names = {
        "company",
        "company_name",
        "name",
        "industry",
        "sector",
        "period",
        "quarter",
        "date",
        "fiscal_year",
        "fiscal year",
        "year",
        "fy",
        "bse_code",
        "nse_code",
        "symbol",
        "ticker",
        "join_key",
    }
    return None if snake in identifier_names else (snake[:80], 1)


def reset_database(db: Session) -> None:
    db.query(FinancialMetric).delete()
    db.query(FinancialPeriod).delete()
    db.query(Company).delete()
    db.commit()


def upsert_company(db: Session, name: str, industry: str = "Middle Market", description: str | None = None) -> Company:
    company = db.scalar(select(Company).where(Company.name == name))
    if company:
        company.industry = industry or company.industry
        company.description = description or company.description
    else:
        company = Company(name=name, industry=industry, description=description)
        db.add(company)
        db.flush()
    return company


def store_period_metrics(db: Session, company: Company, period: str, fiscal_year: int, metrics: dict[str, float | None]) -> None:
    fp = db.scalar(select(FinancialPeriod).where(FinancialPeriod.company_id == company.id, FinancialPeriod.period == period))
    if not fp:
        fp = FinancialPeriod(company_id=company.id, period=period, fiscal_year=fiscal_year)
        db.add(fp)
        db.flush()
    existing = {m.metric_name: m for m in fp.metrics}
    for name, value in metrics.items():
        if name in existing:
            existing[name].value = value
        else:
            db.add(FinancialMetric(period_id=fp.id, metric_name=name, value=value))


def company_metric_rows(db: Session, company_id: int) -> list[dict]:
    periods = db.scalars(select(FinancialPeriod).where(FinancialPeriod.company_id == company_id).order_by(FinancialPeriod.fiscal_year)).all()
    rows: list[dict] = []
    for period in periods:
        row = {"period": period.period, "fiscal_year": period.fiscal_year}
        row.update({metric.metric_name: metric.value for metric in period.metrics})
        rows.append(row)
    return enrich_periods(rows)


def company_summary(db: Session, company: Company) -> dict:
    metrics = company_metric_rows(db, company.id)
    latest = metrics[-1] if metrics else {}
    return {
        "id": company.id,
        "name": company.name,
        "industry": company.industry,
        "description": company.description,
        "latest_period": latest.get("period"),
        "latest_revenue": latest.get("revenue"),
        "latest_ebitda": latest.get("ebitda"),
        "latest_cash": latest.get("cash"),
        "latest_debt": latest.get("total_debt"),
        "revenue_growth": latest.get("revenue_growth"),
        "ebitda_margin": latest.get("ebitda_margin"),
        "current_price": latest.get("current_price"),
        "market_cap": latest.get("market_cap"),
        "pe_ratio": latest.get("pe_ratio"),
        "price_to_book": latest.get("price_to_book"),
        "return_on_equity": latest.get("return_on_equity"),
        "roce": latest.get("roce"),
        "return_1y": latest.get("return_1y"),
        "return_3m": latest.get("return_3m"),
    }


def ingest_dataframe(db: Session, df: pd.DataFrame, default_company: str | None = None) -> dict:
    lower_columns = {str(col).strip().lower(): col for col in df.columns}
    company_col = _first_column(lower_columns, ("company", "company_name", "name", "ticker", "symbol", "nse code", "nse_code"))
    industry_col = _first_column(lower_columns, ("industry", "sector"))
    metric_columns = [(col, mapping[0], mapping[1]) for col in df.columns if (mapping := _metric_mapping(str(col)))]
    if not metric_columns:
        raise ValueError("No numeric financial metric columns were found.")
    companies: set[str] = set()
    metric_names: set[str] = set()
    for _, row in df.iterrows():
        company_name = str(row[company_col]).strip() if company_col and pd.notna(row[company_col]) else default_company
        if not company_name:
            company_name = "Uploaded Financial Data"
        industry = str(row[industry_col]).strip() if industry_col and pd.notna(row[industry_col]) else "Financial Data"
        company = upsert_company(db, company_name, industry)
        metrics = {}
        for source, metric, scale in metric_columns:
            value = _numeric(row[source], scale)
            if value is not None:
                metrics[metric] = value
                metric_names.add(metric)
        if not metrics:
            continue
        period, fiscal_year = _period_parts(row, lower_columns)
        store_period_metrics(db, company, period, fiscal_year, metrics)
        companies.add(company.name)
    db.commit()
    if not companies:
        raise ValueError("No rows with numeric financial metrics were found.")
    return {"companies": sorted(companies), "rows": len(df), "metrics": sorted(metric_names)}


def ingest_upload(db: Session, content: bytes, filename: str, default_company: str | None = None) -> dict:
    if filename.lower().endswith(".xlsx"):
        df = pd.read_excel(BytesIO(content))
    elif filename.lower().endswith(".csv"):
        df = pd.read_csv(BytesIO(content))
    else:
        raise ValueError("Only CSV and XLSX files are supported.")
    return ingest_dataframe(db, df, default_company or Path(filename).stem)


def ingest_archive_dataset(db: Session, data_dir: Path | None = None) -> dict:
    source_dir = data_dir or archive_data_dir()
    files = sorted(source_dir.glob("*.csv"))
    if not files:
        raise ValueError(f"No CSV files found in {source_dir}.")

    merged: pd.DataFrame | None = None
    for path in files:
        frame = pd.read_csv(path)
        if "join_key" not in frame.columns:
            continue
        if merged is None:
            merged = frame
        else:
            merged = merged.merge(frame, on="join_key", how="outer", suffixes=("", f"__{path.stem}"))

    if merged is None or merged.empty:
        raise ValueError("Archive CSVs must include join_key columns.")

    reset_database(db)
    companies: set[str] = set()
    metric_names: set[str] = set()
    for _, row in merged.iterrows():
        name = next((str(row[col]).strip() for col in ("Name", "Name__price_final", "Name__ratios_1_final") if col in merged.columns and pd.notna(row[col])), None)
        if not name:
            continue
        industry = next((str(row[col]).strip() for col in ("Industry", "Industry__price_final", "Industry__ratios_1_final") if col in merged.columns and pd.notna(row[col])), "Listed Equity")
        nse_code = next((str(row[col]).strip() for col in ("NSE Code", "NSE Code__price_final", "NSE Code__ratios_1_final") if col in merged.columns and pd.notna(row[col])), "")
        company = upsert_company(db, name, industry, f"NSE: {nse_code}" if nse_code else None)
        metrics: dict[str, float | None] = {}
        for column in merged.columns:
            source_label = column.split("__", 1)[0]
            mapped = _archive_metric_name(source_label)
            if not mapped:
                continue
            metric, scale = mapped
            value = _numeric(row[column], scale)
            if value is not None and metric not in metrics:
                metrics[metric] = value
        store_period_metrics(db, company, "FY2024", 2024, metrics)
        companies.add(company.name)
        metric_names.update(metrics)
    db.commit()
    return {"companies": sorted(companies), "rows": len(companies), "metrics": sorted(metric_names), "source_dir": str(source_dir)}
