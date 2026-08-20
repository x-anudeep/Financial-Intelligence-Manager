from pydantic import BaseModel


class AnomalyOut(BaseModel):
    id: int
    company_id: int
    company_name: str | None = None
    period: str
    anomaly_type: str
    metric: str
    severity: str
    title: str
    description: str
    current_value: float | None = None
    previous_value: float | None = None
    percentage_change: float | None = None
    evidence: str
    suggested_review: str
    anomaly_score: float | None = None
    method: str
    supporting_statistics: str | None = None

    model_config = {"from_attributes": True}


class PortfolioRiskOverview(BaseModel):
    total_companies: int
    total_anomalies: int
    high_risk_exceptions: int
    critical_exceptions: int
    severity_distribution: dict[str, int]
    anomaly_categories: dict[str, int]
    companies_requiring_review: list[dict]


class CompanyComparison(BaseModel):
    companies: list[dict]
