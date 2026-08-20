from __future__ import annotations

import json
import os
from pathlib import Path
from datetime import date

import httpx
import pandas as pd
from sqlalchemy.orm import Session

from app.services.financials import ingest_dataframe

SEC_TICKERS_URL = "https://www.sec.gov/files/company_tickers.json"
SEC_FACTS_URL = "https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"

METRIC_TAGS: dict[str, list[str]] = {
    "revenue": ["RevenueFromContractWithCustomerExcludingAssessedTax", "Revenues", "SalesRevenueNet", "SalesRevenueGoodsNet"],
    "cogs": ["CostOfRevenue", "CostOfGoodsAndServicesSold"],
    "gross_profit": ["GrossProfit"],
    "operating_expenses": ["OperatingExpenses"],
    "ebit": ["OperatingIncomeLoss", "IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest"],
    "net_income": ["NetIncomeLoss", "ProfitLoss"],
    "cash": ["CashAndDueFromBanks", "CashAndCashEquivalentsAtCarryingValue", "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents"],
    "accounts_receivable": ["AccountsReceivableNetCurrent"],
    "inventory": ["InventoryNet"],
    "accounts_payable": ["AccountsPayableCurrent"],
    "current_assets": ["AssetsCurrent"],
    "current_liabilities": ["LiabilitiesCurrent"],
    "total_assets": ["Assets"],
    "total_debt": [
        "DebtCurrent",
        "LongTermDebtCurrent",
        "LongTermDebtNoncurrent",
        "LongTermDebt",
        "ShortTermBorrowings",
        "FederalFundsPurchasedAndSecuritiesSoldUnderAgreementsToRepurchase",
    ],
    "total_equity": ["StockholdersEquity", "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest"],
    "operating_cash_flow": ["NetCashProvidedByUsedInOperatingActivities"],
    "capital_expenditure": ["PaymentsToAcquirePropertyPlantAndEquipment"],
    "interest_expense": ["InterestExpenseNonOperating", "InterestExpense"],
    "eps": ["EarningsPerShareDiluted"],
    "interest_income": ["InterestAndDividendIncomeOperating"],
    "net_interest_income": ["InterestIncomeExpenseNet"],
    "noninterest_income": ["NoninterestIncome"],
    "noninterest_expense": ["NoninterestExpense"],
    "loan_loss_provision": ["ProvisionForLoanLeaseAndOtherLosses", "ProvisionForLoanAndLeaseLosses", "ProvisionForLoanLossesExpensed"],
    "deposits": ["Deposits"],
    "loans": ["LoansAndLeasesReceivableNetReportedAmount", "FinancingReceivableExcludingAccruedInterestAfterAllowanceForCreditLoss"],
    "investment_securities": ["DebtSecuritiesAvailableForSaleExcludingAccruedInterest", "AvailableForSaleSecuritiesDebtSecurities"],
}

FLOW_METRICS = {
    "revenue",
    "cogs",
    "gross_profit",
    "operating_expenses",
    "ebit",
    "net_income",
    "operating_cash_flow",
    "capital_expenditure",
    "interest_expense",
    "eps",
    "interest_income",
    "net_interest_income",
    "noninterest_income",
    "noninterest_expense",
    "loan_loss_provision",
}

AGGREGATE_METRICS = {"total_debt"}
FILL_FROM_ALL_TAGS = {"loans", "loan_loss_provision", "investment_securities"}


def fetch_sec_company(db: Session, query: str) -> dict:
    company = _find_company(query)
    facts = _get_json(SEC_FACTS_URL.format(cik=company["cik"]))
    rows = _facts_to_rows(facts, company)
    if not rows:
        raise ValueError(f"No annual SEC facts could be parsed for {company['title']}.")
    df = pd.DataFrame(rows).sort_values("fiscal_year")
    out_dir = Path(__file__).resolve().parents[3] / "data" / "real_company_csvs"
    out_dir.mkdir(parents=True, exist_ok=True)
    csv_path = out_dir / f"{company['ticker'].lower()}_sec_financials.csv"
    df.to_csv(csv_path, index=False)
    result = ingest_dataframe(db, df)
    result.update({
        "source": "SEC EDGAR CompanyFacts",
        "ticker": company["ticker"],
        "cik": company["cik"],
        "company": company["title"],
        "csv_path": str(csv_path),
    })
    return result


def _headers() -> dict[str, str]:
    return {
        "User-Agent": os.getenv("SEC_USER_AGENT", "FinancialIntelligenceManager/1.0 contact@example.com"),
    }


def _get_json(url: str) -> dict:
    try:
        response = httpx.get(url, headers=_headers(), timeout=30, follow_redirects=True)
        response.raise_for_status()
        return json.loads(response.text)
    except httpx.HTTPStatusError as exc:
        raise ValueError(f"SEC request failed with HTTP {exc.response.status_code}. Try a ticker like AAPL, MSFT, JPM, or TSLA.") from exc
    except httpx.RequestError as exc:
        raise ValueError("Could not reach SEC EDGAR. Check internet access and try again.") from exc


def _find_company(query: str) -> dict[str, str]:
    term = query.strip().lower()
    if not term:
        raise ValueError("Enter a company name or ticker.")
    tickers = _get_json(SEC_TICKERS_URL)
    rows = list(tickers.values())
    exact = [row for row in rows if str(row.get("ticker", "")).lower() == term]
    contains = [row for row in rows if term in str(row.get("title", "")).lower() or term in str(row.get("ticker", "")).lower()]
    matches = exact or contains
    if not matches:
        raise ValueError(f"No SEC public company match found for '{query}'. Try a US ticker such as AAPL, MSFT, JPM, or TSLA.")
    row = matches[0]
    return {
        "ticker": str(row["ticker"]).upper(),
        "title": str(row["title"]),
        "cik": str(row["cik_str"]).zfill(10),
    }


def _facts_to_rows(facts: dict, company: dict[str, str]) -> list[dict]:
    us_gaap = facts.get("facts", {}).get("us-gaap", {})
    by_year: dict[int, dict] = {}
    for metric, tags in METRIC_TAGS.items():
        for tag in tags:
            units = us_gaap.get(tag, {}).get("units", {})
            unit_rows = units.get("USD") or units.get("USD/shares") or units.get("shares")
            if not unit_rows:
                continue
            added = False
            for item in unit_rows:
                if item.get("form") not in {"10-K", "20-F", "40-F"}:
                    continue
                if item.get("fp") != "FY":
                    continue
                frame = str(item.get("frame", ""))
                year = _flow_year(item) if metric in FLOW_METRICS else _instant_year(item)
                value = item.get("val")
                if not year or value is None:
                    continue
                if metric in FLOW_METRICS:
                    expected_frame = f"CY{int(year)}"
                    if frame and ("Q" in frame or frame != expected_frame):
                        continue
                    if not frame and str(item.get("end", ""))[:4] != str(year):
                        continue
                    if not _is_annual_duration(item):
                        continue
                elif frame and frame not in {f"CY{int(year)}", f"CY{int(year)}Q4I"}:
                    continue
                row = by_year.setdefault(int(year), {
                    "company": company["title"],
                    "industry": f"SEC filer ({company['ticker']})",
                    "period": f"FY{int(year)}",
                    "fiscal_year": int(year),
                })
                if metric in AGGREGATE_METRICS and metric in row:
                    row[metric] += float(value)
                elif metric not in row:
                    row[metric] = abs(float(value)) if metric == "capital_expenditure" else float(value)
                    added = True
            if added and metric not in AGGREGATE_METRICS and metric not in FILL_FROM_ALL_TAGS:
                break
    rows = [row for _, row in sorted(by_year.items()) if len(row) > 5]
    for row in rows:
        if "ebit" in row and "ebitda" not in row:
            row["ebitda"] = row["ebit"]
    return rows[-6:]


def _flow_year(item: dict) -> int | None:
    year = item.get("fy")
    return int(year) if year else None


def _instant_year(item: dict) -> int | None:
    end = item.get("end")
    if end:
        return int(str(end)[:4])
    year = item.get("fy")
    return int(year) if year else None


def _is_annual_duration(item: dict) -> bool:
    start = item.get("start")
    end = item.get("end")
    if not start or not end:
        return False
    try:
        start_date = date.fromisoformat(str(start))
        end_date = date.fromisoformat(str(end))
    except ValueError:
        return False
    duration_days = (end_date - start_date).days
    return 330 <= duration_days <= 380
