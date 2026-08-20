from dataclasses import dataclass


@dataclass(frozen=True)
class Thresholds:
    revenue_decline: float = -0.03
    ebitda_margin_compression: float = -0.03
    ar_revenue_growth_spread: float = 0.30
    inventory_revenue_growth_spread: float = 0.25
    debt_ebitda_growth_spread: float = 0.25
    cash_deterioration: float = -0.20
    ocf_conversion_weak: float = 0.60
    interest_coverage_weak: float = 2.0
    expense_spike: float = 0.20
    abnormal_yoy_movement: float = 0.35
    working_capital_deterioration: float = -0.20
    ebitda_lag_revenue_spread: float = -0.20
    z_score_min_periods: int = 5
    z_score_threshold: float = 1.8


thresholds = Thresholds()
