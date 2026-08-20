from io import BytesIO

import pandas as pd
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.financial_engine.calculations import enrich_periods
from app.financial_engine.labels import normalize_label
from app.models.financial import Company, FinancialMetric, FinancialPeriod


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
    }


def ingest_dataframe(db: Session, df: pd.DataFrame, default_company: str | None = None) -> dict:
    required = {"period", "fiscal_year"}
    lower_columns = {str(col).strip().lower(): col for col in df.columns}
    if not required.issubset(lower_columns):
        raise ValueError("Upload must include period and fiscal_year columns.")
    company_col = lower_columns.get("company") or lower_columns.get("company_name")
    industry_col = lower_columns.get("industry")
    metric_columns = [(col, normalize_label(str(col))) for col in df.columns]
    metric_columns = [(col, metric) for col, metric in metric_columns if metric]
    if not metric_columns:
        raise ValueError("No recognized financial metric columns were found.")
    companies: set[str] = set()
    for _, row in df.iterrows():
        company_name = str(row[company_col]).strip() if company_col else default_company
        if not company_name:
            raise ValueError("Upload must include a company column or target company.")
        industry = str(row[industry_col]).strip() if industry_col else "Middle Market"
        company = upsert_company(db, company_name, industry)
        metrics = {}
        for source, metric in metric_columns:
            value = pd.to_numeric(row[source], errors="coerce")
            metrics[metric] = None if pd.isna(value) else float(value)
        fiscal_year = int(row[lower_columns["fiscal_year"]])
        store_period_metrics(db, company, str(row[lower_columns["period"]]), fiscal_year, metrics)
        companies.add(company.name)
    db.commit()
    return {"companies": sorted(companies), "rows": len(df), "metrics": sorted({metric for _, metric in metric_columns})}


def ingest_upload(db: Session, content: bytes, filename: str, default_company: str | None = None) -> dict:
    if filename.lower().endswith(".xlsx"):
        df = pd.read_excel(BytesIO(content))
    elif filename.lower().endswith(".csv"):
        df = pd.read_csv(BytesIO(content))
    else:
        raise ValueError("Only CSV and XLSX files are supported.")
    return ingest_dataframe(db, df, default_company)
