from app.financial_engine.calculations import enrich_periods, pct_change, safe_div
from app.financial_engine.labels import normalize_label


def test_safe_division_handles_zero_and_missing():
    assert safe_div(10, 2) == 5
    assert safe_div(10, 0) is None
    assert safe_div(None, 2) is None


def test_pct_change_formula():
    assert pct_change(120, 100) == 0.2
    assert pct_change(120, 0) is None


def test_label_normalization():
    assert normalize_label("Net Sales") == "revenue"
    assert normalize_label("A/R") == "accounts_receivable"
    assert normalize_label("unknown label") is None


def test_enrich_periods_calculates_ratios_and_growth():
    rows = [
        {"period": "FY2024", "fiscal_year": 2024, "revenue": 100, "gross_profit": 40, "ebitda": 15, "cash": 10, "total_debt": 30, "current_assets": 50, "current_liabilities": 25, "inventory": 10},
        {"period": "FY2025", "fiscal_year": 2025, "revenue": 125, "gross_profit": 45, "ebitda": 20, "cash": 9, "total_debt": 40, "current_assets": 54, "current_liabilities": 30, "inventory": 11},
    ]
    enriched = enrich_periods(rows)
    assert enriched[0]["gross_margin"] == 0.4
    assert enriched[1]["revenue_growth"] == 0.25
    assert enriched[1]["debt_to_ebitda"] == 2
