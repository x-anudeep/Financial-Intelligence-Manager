from statistics import mean, pstdev

from app.anomaly_engine.thresholds import thresholds

SEVERITY_WEIGHT = {"low": 1, "medium": 2, "high": 3, "critical": 4}


def pct(value: float | None) -> str:
    return "N/A" if value is None else f"{value * 100:.1f}%"


def money(value: float | None) -> str:
    return "N/A" if value is None else f"${value / 1_000_000:.1f}M"


def severity_for(spread: float | None, high: float, critical: float) -> str:
    if spread is None:
        return "medium"
    absolute = abs(spread)
    if absolute >= critical:
        return "critical"
    if absolute >= high:
        return "high"
    return "medium"


def anomaly(period: str, anomaly_type: str, metric: str, severity: str, title: str, description: str, current_value: float | None, previous_value: float | None, percentage_change: float | None, evidence: str, suggested: list[str], method: str = "rule", score: float | None = None, stats: str | None = None) -> dict:
    return {
        "period": period,
        "anomaly_type": anomaly_type,
        "metric": metric,
        "severity": severity,
        "title": title,
        "description": description,
        "current_value": current_value,
        "previous_value": previous_value,
        "percentage_change": percentage_change,
        "evidence": evidence,
        "suggested_review": "\n".join(suggested),
        "method": method,
        "anomaly_score": score,
        "supporting_statistics": stats,
    }


def detect_rule_anomalies(rows: list[dict]) -> list[dict]:
    findings: list[dict] = []
    ordered = sorted(rows, key=lambda row: row["fiscal_year"])
    for index, row in enumerate(ordered):
        if index == 0:
            continue
        previous = ordered[index - 1]
        period = row["period"]
        revenue_growth = row.get("revenue_growth")
        ebitda_growth = row.get("ebitda_growth")
        if revenue_growth is not None and revenue_growth < thresholds.revenue_decline:
            findings.append(anomaly(period, "revenue_decline", "revenue", severity_for(revenue_growth, 0.08, 0.15), "Revenue decline identified", "Revenue declined year over year and requires analyst review.", row.get("revenue"), previous.get("revenue"), revenue_growth, f"Revenue changed from {money(previous.get('revenue'))} to {money(row.get('revenue'))}, a YoY change of {pct(revenue_growth)}.", ["Demand trends", "Pricing changes", "Customer concentration", "Lost contracts"]))
        margin_change = None if row.get("ebitda_margin") is None or previous.get("ebitda_margin") is None else row["ebitda_margin"] - previous["ebitda_margin"]
        if margin_change is not None and margin_change < thresholds.ebitda_margin_compression:
            findings.append(anomaly(period, "margin_compression", "ebitda_margin", severity_for(margin_change, 0.04, 0.07), "EBITDA margin compression", "EBITDA margin deteriorated from the prior period.", row.get("ebitda_margin"), previous.get("ebitda_margin"), margin_change, f"EBITDA margin moved from {pct(previous.get('ebitda_margin'))} to {pct(row.get('ebitda_margin'))}, a change of {pct(margin_change)}.", ["Gross margin bridge", "Labor or input cost inflation", "Operating expense run-rate", "One-time expenses"]))
        ar_spread = None if row.get("accounts_receivable_growth") is None or revenue_growth is None else row["accounts_receivable_growth"] - revenue_growth
        if ar_spread is not None and ar_spread > thresholds.ar_revenue_growth_spread:
            findings.append(anomaly(period, "working_capital", "accounts_receivable", severity_for(ar_spread, 0.45, 0.65), "Receivables growth exception", "Receivables increased materially faster than revenue.", row.get("accounts_receivable"), previous.get("accounts_receivable"), row.get("accounts_receivable_growth"), f"AR growth was {pct(row.get('accounts_receivable_growth'))}; revenue growth was {pct(revenue_growth)}; spread was {pct(ar_spread)}.", ["Days sales outstanding", "Payment-term changes", "Receivables aging", "Customer concentration"]))
        inventory_spread = None if row.get("inventory_growth") is None or revenue_growth is None else row["inventory_growth"] - revenue_growth
        if inventory_spread is not None and inventory_spread > thresholds.inventory_revenue_growth_spread:
            findings.append(anomaly(period, "working_capital", "inventory", severity_for(inventory_spread, 0.40, 0.60), "Inventory growth exception", "Inventory increased materially faster than revenue.", row.get("inventory"), previous.get("inventory"), row.get("inventory_growth"), f"Inventory growth was {pct(row.get('inventory_growth'))}; revenue growth was {pct(revenue_growth)}; spread was {pct(inventory_spread)}.", ["Inventory aging", "Forecast changes", "Supply-chain purchases", "Obsolescence exposure"]))
        debt_spread = None if row.get("debt_growth") is None or ebitda_growth is None else row["debt_growth"] - ebitda_growth
        if debt_spread is not None and debt_spread > thresholds.debt_ebitda_growth_spread:
            findings.append(anomaly(period, "leverage", "total_debt", severity_for(debt_spread, 0.45, 0.70), "Debt growth outpaced EBITDA", "Debt increased faster than EBITDA, indicating potential leverage pressure.", row.get("total_debt"), previous.get("total_debt"), row.get("debt_growth"), f"Debt growth was {pct(row.get('debt_growth'))}; EBITDA growth was {pct(ebitda_growth)}; spread was {pct(debt_spread)}.", ["Debt schedule", "Covenant headroom", "Acquisition financing", "EBITDA adjustments"]))
        if row.get("cash_change") is not None and row["cash_change"] < thresholds.cash_deterioration:
            findings.append(anomaly(period, "liquidity", "cash", severity_for(row["cash_change"], 0.25, 0.40), "Significant cash deterioration", "Cash declined materially from the prior period.", row.get("cash"), previous.get("cash"), row.get("cash_change"), f"Cash changed from {money(previous.get('cash'))} to {money(row.get('cash'))}, a change of {pct(row.get('cash_change'))}.", ["Cash flow statement", "Debt amortization", "Capital expenditures", "Working-capital usage"]))
        if row.get("operating_cash_flow_to_ebitda") is not None and row["operating_cash_flow_to_ebitda"] < thresholds.ocf_conversion_weak:
            findings.append(anomaly(period, "cash_generation", "operating_cash_flow", "high" if row["operating_cash_flow_to_ebitda"] < 0.35 else "medium", "Weak operating cash conversion", "Operating cash flow is weak relative to EBITDA.", row.get("operating_cash_flow"), row.get("ebitda"), row.get("operating_cash_flow_to_ebitda"), f"Operating cash flow / EBITDA was {pct(row.get('operating_cash_flow_to_ebitda'))}.", ["Working-capital movements", "One-time cash costs", "Revenue quality", "Collections timing"]))
        if row.get("interest_coverage") is not None and row["interest_coverage"] < thresholds.interest_coverage_weak:
            findings.append(anomaly(period, "leverage", "interest_coverage", "high" if row["interest_coverage"] < 1.25 else "medium", "Weakening interest coverage", "EBIT coverage of interest expense is low.", row.get("interest_coverage"), previous.get("interest_coverage"), None, f"Interest coverage was {row.get('interest_coverage'):.2f}x versus review threshold of {thresholds.interest_coverage_weak:.2f}x.", ["Rate exposure", "Debt maturity schedule", "EBIT adjustments", "Covenant definitions"]))
        expense_growth = None if row.get("operating_expenses") is None or previous.get("operating_expenses") in (None, 0) else (row["operating_expenses"] - previous["operating_expenses"]) / previous["operating_expenses"]
        if expense_growth is not None and revenue_growth is not None and expense_growth - revenue_growth > thresholds.expense_spike:
            findings.append(anomaly(period, "expense_spike", "operating_expenses", severity_for(expense_growth - revenue_growth, 0.35, 0.55), "Unusual operating expense spike", "Operating expenses increased materially faster than revenue.", row.get("operating_expenses"), previous.get("operating_expenses"), expense_growth, f"Operating expense growth was {pct(expense_growth)}; revenue growth was {pct(revenue_growth)}.", ["Expense detail", "Legal or professional fees", "Headcount additions", "One-time charges"]))
        if row.get("working_capital_growth") is not None and row["working_capital_growth"] < thresholds.working_capital_deterioration:
            findings.append(anomaly(period, "working_capital", "working_capital", severity_for(row["working_capital_growth"], 0.35, 0.55), "Working-capital deterioration", "Working capital declined materially from the prior period.", row.get("working_capital"), previous.get("working_capital"), row.get("working_capital_growth"), f"Working capital changed from {money(previous.get('working_capital'))} to {money(row.get('working_capital'))}, a change of {pct(row.get('working_capital_growth'))}.", ["AR aging", "Inventory levels", "Vendor payments", "Short-term liquidity"]))
        lag = None if ebitda_growth is None or revenue_growth is None else ebitda_growth - revenue_growth
        if lag is not None and lag < thresholds.ebitda_lag_revenue_spread:
            findings.append(anomaly(period, "profitability", "ebitda", severity_for(lag, 0.30, 0.50), "EBITDA growth lagged revenue", "EBITDA growth materially lagged revenue growth.", row.get("ebitda"), previous.get("ebitda"), ebitda_growth, f"EBITDA growth was {pct(ebitda_growth)} while revenue growth was {pct(revenue_growth)}; gap was {pct(lag)}.", ["Cost inflation", "Pricing discipline", "Operating leverage", "One-time costs"]))
    return findings


def detect_statistical_anomalies(rows: list[dict]) -> list[dict]:
    if len(rows) < thresholds.z_score_min_periods:
        return []
    findings: list[dict] = []
    metrics = ["revenue", "ebitda", "cash", "accounts_receivable", "inventory", "total_debt", "operating_cash_flow"]
    latest = sorted(rows, key=lambda row: row["fiscal_year"])[-1]
    history = sorted(rows, key=lambda row: row["fiscal_year"])[:-1]
    for metric in metrics:
        values = [row.get(metric) for row in history if row.get(metric) is not None]
        if len(values) < thresholds.z_score_min_periods - 1:
            continue
        sigma = pstdev(values)
        if sigma == 0:
            continue
        z_score = (latest.get(metric) - mean(values)) / sigma if latest.get(metric) is not None else None
        if z_score is not None and abs(z_score) >= thresholds.z_score_threshold:
            findings.append(anomaly(latest["period"], "statistical_movement", metric, severity_for(z_score / 10, 0.25, 0.35), "Abnormal year-over-year metric movement", "Latest value is statistically unusual relative to available company history.", latest.get(metric), values[-1], None, f"{metric} z-score was {z_score:.2f} using {len(values)} historical observations.", ["Confirm non-recurring events", "Review source statement mapping", "Compare against budget", "Assess operating drivers"], method="z_score", score=abs(z_score), stats=f"mean={mean(values):.2f}; stdev={sigma:.2f}; z={z_score:.2f}"))
    return findings


def detect_anomalies(rows: list[dict]) -> list[dict]:
    return detect_rule_anomalies(rows) + detect_statistical_anomalies(rows)
