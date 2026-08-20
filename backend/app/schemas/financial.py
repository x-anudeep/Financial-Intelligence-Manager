from pydantic import BaseModel


class MetricPoint(BaseModel):
    period: str
    fiscal_year: int
    revenue: float | None = None
    gross_profit: float | None = None
    ebitda: float | None = None
    net_income: float | None = None
    cash: float | None = None
    accounts_receivable: float | None = None
    inventory: float | None = None
    accounts_payable: float | None = None
    current_assets: float | None = None
    current_liabilities: float | None = None
    total_debt: float | None = None
    operating_cash_flow: float | None = None
    gross_margin: float | None = None
    ebitda_margin: float | None = None
    net_margin: float | None = None
    current_ratio: float | None = None
    quick_ratio: float | None = None
    debt_to_ebitda: float | None = None
    operating_cash_flow_to_ebitda: float | None = None
    revenue_growth: float | None = None
    ebitda_growth: float | None = None
    cash_change: float | None = None
    debt_growth: float | None = None
    working_capital: float | None = None
    working_capital_growth: float | None = None


class CompanySummary(BaseModel):
    id: int
    name: str
    industry: str
    description: str | None = None
    latest_period: str | None = None
    latest_revenue: float | None = None
    latest_ebitda: float | None = None
    latest_cash: float | None = None
    latest_debt: float | None = None
    revenue_growth: float | None = None
    ebitda_margin: float | None = None


class CompanyDetail(CompanySummary):
    metrics: list[MetricPoint]
    anomalies: list[dict] = []
