import random
import os
from pathlib import Path

import pandas as pd
from sqlalchemy.orm import Session

from app.services.financials import ingest_dataframe, reset_database

INDUSTRIES = ["Manufacturing", "Business Services", "Distribution", "Healthcare Services", "Food & Beverage", "Industrial Technology"]


def generate_synthetic_financials(company_count: int = 36, start_year: int = 2021, years: int = 5) -> pd.DataFrame:
    random.seed(42)
    profiles = ["healthy", "growth", "leveraged", "declining", "working_capital", "receivables", "cash_flow", "expense_spike"]
    rows = []
    for idx in range(company_count):
        profile = profiles[idx % len(profiles)]
        name = f"{['Apex','Titan','Summit','Northstar','Atlas','Pioneer'][idx % 6]} {idx + 1:02d}"
        industry = INDUSTRIES[idx % len(INDUSTRIES)]
        revenue = random.uniform(45_000_000, 180_000_000)
        cash = revenue * random.uniform(0.05, 0.13)
        debt = revenue * random.uniform(0.15, 0.55)
        ar = revenue * random.uniform(0.09, 0.17)
        inventory = revenue * random.uniform(0.08, 0.18)
        for offset in range(years):
            year = start_year + offset
            growth = random.uniform(0.04, 0.12)
            if profile == "growth":
                growth = random.uniform(0.16, 0.28)
            if profile == "declining" and offset >= 2:
                growth = random.uniform(-0.12, -0.03)
            revenue *= 1 + growth
            gross_margin = random.uniform(0.31, 0.45)
            ebitda_margin = random.uniform(0.10, 0.19)
            if profile == "expense_spike" and offset == years - 1:
                ebitda_margin -= 0.08
            if profile == "declining" and offset >= 3:
                ebitda_margin -= 0.04
            ebitda = revenue * max(0.02, ebitda_margin)
            gross_profit = revenue * gross_margin
            operating_expenses = max(gross_profit - ebitda, 0)
            ebit = ebitda * 0.82
            interest_expense = max(debt * random.uniform(0.045, 0.085), 150_000)
            net_income = ebit - interest_expense - revenue * 0.015
            if profile == "receivables" and offset == years - 1:
                ar *= 1.65
            else:
                ar *= 1 + growth + random.uniform(-0.02, 0.04)
            if profile == "working_capital" and offset >= years - 2:
                inventory *= 1.25
            else:
                inventory *= 1 + growth + random.uniform(-0.02, 0.03)
            ap = revenue * random.uniform(0.07, 0.13)
            current_assets = cash + ar + inventory + revenue * 0.05
            current_liabilities = ap + revenue * random.uniform(0.10, 0.18)
            if profile == "working_capital" and offset == years - 1:
                current_liabilities *= 1.55
            if profile == "leveraged" and offset >= 2:
                debt *= 1.22
            else:
                debt *= 1 + random.uniform(-0.04, 0.08)
            if profile == "cash_flow" and offset >= years - 2:
                operating_cash_flow = ebitda * random.uniform(0.25, 0.45)
                cash *= 0.74
            else:
                operating_cash_flow = ebitda * random.uniform(0.70, 1.05)
                cash *= 1 + random.uniform(-0.05, 0.12)
            rows.append({
                "company": name,
                "industry": industry,
                "period": f"FY{year}",
                "fiscal_year": year,
                "revenue": round(revenue, 2),
                "cogs": round(revenue - gross_profit, 2),
                "gross_profit": round(gross_profit, 2),
                "operating_expenses": round(operating_expenses, 2),
                "ebitda": round(ebitda, 2),
                "ebit": round(ebit, 2),
                "net_income": round(net_income, 2),
                "cash": round(cash, 2),
                "accounts_receivable": round(ar, 2),
                "inventory": round(inventory, 2),
                "accounts_payable": round(ap, 2),
                "current_assets": round(current_assets, 2),
                "current_liabilities": round(current_liabilities, 2),
                "total_assets": round(current_assets + revenue * random.uniform(0.45, 0.85), 2),
                "total_debt": round(debt, 2),
                "total_equity": round(revenue * random.uniform(0.22, 0.55), 2),
                "operating_cash_flow": round(operating_cash_flow, 2),
                "capital_expenditure": round(revenue * random.uniform(0.015, 0.045), 2),
                "interest_expense": round(interest_expense, 2),
            })
    return pd.DataFrame(rows)


def seed_database(db: Session) -> dict:
    reset_database(db)
    df = generate_synthetic_financials()
    result = ingest_dataframe(db, df)
    configured = os.getenv("SAMPLE_DATA_DIR")
    data_dir = Path(configured) if configured else Path(__file__).resolve().parents[3] / "data"
    data_dir.mkdir(exist_ok=True)
    df.to_csv(data_dir / "sample_financials.csv", index=False)
    return result
