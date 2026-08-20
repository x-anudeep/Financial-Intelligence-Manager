SUPPORTED_METRICS = {
    "revenue",
    "cogs",
    "gross_profit",
    "operating_expenses",
    "ebitda",
    "ebit",
    "net_income",
    "cash",
    "accounts_receivable",
    "inventory",
    "accounts_payable",
    "current_assets",
    "current_liabilities",
    "total_assets",
    "total_debt",
    "total_equity",
    "operating_cash_flow",
    "capital_expenditure",
    "interest_expense",
}

LABEL_MAP = {
    "sales": "revenue",
    "net sales": "revenue",
    "total revenue": "revenue",
    "revenue": "revenue",
    "cogs": "cogs",
    "cost of goods sold": "cogs",
    "gross profit": "gross_profit",
    "operating expenses": "operating_expenses",
    "opex": "operating_expenses",
    "ebitda": "ebitda",
    "ebit": "ebit",
    "net income": "net_income",
    "cash": "cash",
    "cash and equivalents": "cash",
    "accounts receivable": "accounts_receivable",
    "a/r": "accounts_receivable",
    "trade receivables": "accounts_receivable",
    "inventory": "inventory",
    "accounts payable": "accounts_payable",
    "a/p": "accounts_payable",
    "current assets": "current_assets",
    "current liabilities": "current_liabilities",
    "total assets": "total_assets",
    "total debt": "total_debt",
    "debt": "total_debt",
    "total equity": "total_equity",
    "operating cash flow": "operating_cash_flow",
    "cash flow from operations": "operating_cash_flow",
    "capex": "capital_expenditure",
    "capital expenditure": "capital_expenditure",
    "interest expense": "interest_expense",
}


def normalize_label(label: str) -> str | None:
    key = " ".join(str(label).strip().lower().replace("_", " ").split())
    if key in LABEL_MAP:
        return LABEL_MAP[key]
    snake = key.replace(" ", "_")
    return snake if snake in SUPPORTED_METRICS else None
