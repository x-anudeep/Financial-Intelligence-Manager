from math import isfinite


def safe_div(numerator: float | None, denominator: float | None) -> float | None:
    if numerator is None or denominator in (None, 0):
        return None
    result = numerator / denominator
    return result if isfinite(result) else None


def pct_change(current: float | None, previous: float | None) -> float | None:
    if current is None or previous in (None, 0):
        return None
    return (current - previous) / previous


def cagr(first: float | None, last: float | None, periods: int) -> float | None:
    if first is None or last is None or first <= 0 or last <= 0 or periods <= 0:
        return None
    return (last / first) ** (1 / periods) - 1


def enrich_periods(rows: list[dict]) -> list[dict]:
    ordered = sorted(rows, key=lambda item: item["fiscal_year"])
    for index, row in enumerate(ordered):
        revenue = row.get("revenue")
        ebitda = row.get("ebitda")
        current_assets = row.get("current_assets")
        current_liabilities = row.get("current_liabilities")
        inventory = row.get("inventory")
        cash = row.get("cash")
        debt = row.get("total_debt")
        ocf = row.get("operating_cash_flow")
        net_interest_income = row.get("net_interest_income")
        interest_income = row.get("interest_income")
        interest_expense = row.get("interest_expense")
        noninterest_income = row.get("noninterest_income")
        noninterest_expense = row.get("noninterest_expense")
        loans = row.get("loans")
        deposits = row.get("deposits")
        total_assets = row.get("total_assets")
        total_equity = row.get("total_equity")
        if net_interest_income is None and interest_income is not None and interest_expense is not None:
            net_interest_income = interest_income - interest_expense
            row["net_interest_income"] = net_interest_income
        row["gross_margin"] = safe_div(row.get("gross_profit"), revenue)
        row["ebitda_margin"] = safe_div(ebitda, revenue)
        row["net_margin"] = safe_div(row.get("net_income"), revenue)
        row["current_ratio"] = safe_div(current_assets, current_liabilities)
        row["quick_ratio"] = safe_div((current_assets or 0) - (inventory or 0), current_liabilities) if current_assets is not None else None
        row["debt_to_ebitda"] = safe_div(debt, ebitda)
        row["interest_coverage"] = safe_div(row.get("ebit"), row.get("interest_expense"))
        row["operating_cash_flow_to_ebitda"] = safe_div(ocf, ebitda)
        row["working_capital"] = current_assets - current_liabilities if current_assets is not None and current_liabilities is not None else None
        bank_revenue_base = (net_interest_income or 0) + (noninterest_income or 0)
        row["loan_to_deposit"] = safe_div(loans, deposits)
        row["efficiency_ratio"] = safe_div(noninterest_expense, bank_revenue_base if bank_revenue_base else None)
        row["provision_to_loans"] = safe_div(row.get("loan_loss_provision"), loans)
        row["return_on_assets"] = safe_div(row.get("net_income"), total_assets)
        row["return_on_equity"] = safe_div(row.get("net_income"), total_equity)
        if index > 0:
            previous = ordered[index - 1]
            row["revenue_growth"] = pct_change(revenue, previous.get("revenue"))
            row["ebitda_growth"] = pct_change(ebitda, previous.get("ebitda"))
            row["accounts_receivable_growth"] = pct_change(row.get("accounts_receivable"), previous.get("accounts_receivable"))
            row["inventory_growth"] = pct_change(inventory, previous.get("inventory"))
            row["accounts_payable_growth"] = pct_change(row.get("accounts_payable"), previous.get("accounts_payable"))
            row["cash_change"] = pct_change(cash, previous.get("cash"))
            row["debt_growth"] = pct_change(debt, previous.get("total_debt"))
            row["working_capital_growth"] = pct_change(row.get("working_capital"), previous.get("working_capital"))
            row["deposit_growth"] = pct_change(deposits, previous.get("deposits"))
            row["loan_growth"] = pct_change(loans, previous.get("loans"))
            row["net_income_growth"] = pct_change(row.get("net_income"), previous.get("net_income"))
        else:
            row.update({
                "revenue_growth": None,
                "ebitda_growth": None,
                "accounts_receivable_growth": None,
                "inventory_growth": None,
                "accounts_payable_growth": None,
                "cash_change": None,
                "debt_growth": None,
                "working_capital_growth": None,
                "deposit_growth": None,
                "loan_growth": None,
                "net_income_growth": None,
            })
    if len(ordered) >= 3:
        periods = ordered[-1]["fiscal_year"] - ordered[0]["fiscal_year"]
        ordered[-1]["revenue_cagr"] = cagr(ordered[0].get("revenue"), ordered[-1].get("revenue"), periods)
    return ordered
