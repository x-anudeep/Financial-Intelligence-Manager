from app.anomaly_engine.detectors import detect_anomalies
from app.financial_engine.calculations import enrich_periods


def test_receivables_growth_spread_is_explainable():
    rows = enrich_periods([
        {"period": "FY2024", "fiscal_year": 2024, "revenue": 91_000_000, "accounts_receivable": 14_100_000, "ebitda": 12_000_000, "current_assets": 35_000_000, "current_liabilities": 20_000_000},
        {"period": "FY2025", "fiscal_year": 2025, "revenue": 103_000_000, "accounts_receivable": 24_800_000, "ebitda": 13_000_000, "current_assets": 42_000_000, "current_liabilities": 21_000_000},
    ])
    findings = detect_anomalies(rows)
    ar = next(item for item in findings if item["metric"] == "accounts_receivable")
    assert ar["anomaly_type"] == "working_capital"
    assert round(ar["percentage_change"], 3) == 0.759
    assert "spread was 62.7%" in ar["evidence"]


def test_tiny_history_does_not_force_statistical_detection():
    rows = enrich_periods([
        {"period": "FY2024", "fiscal_year": 2024, "revenue": 100, "ebitda": 10},
        {"period": "FY2025", "fiscal_year": 2025, "revenue": 101, "ebitda": 10},
    ])
    findings = detect_anomalies(rows)
    assert all(item["method"] != "z_score" for item in findings)
