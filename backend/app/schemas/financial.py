from pydantic import BaseModel, ConfigDict


class MetricPoint(BaseModel):
    model_config = ConfigDict(extra="allow")

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
    current_price: float | None = None
    market_cap: float | None = None
    eps: float | None = None
    pe_ratio: float | None = None
    price_to_book: float | None = None
    price_to_sales: float | None = None
    dividend_yield: float | None = None
    return_on_equity: float | None = None
    return_on_assets: float | None = None
    roce: float | None = None
    debt_to_equity: float | None = None
    promoter_holding: float | None = None
    fii_holding: float | None = None
    dii_holding: float | None = None
    sales_growth_3y: float | None = None
    sales_growth_5y: float | None = None
    profit_growth_3y: float | None = None
    profit_growth_5y: float | None = None
    return_1d: float | None = None
    return_1w: float | None = None
    return_1m: float | None = None
    return_3m: float | None = None
    return_6m: float | None = None
    return_1y: float | None = None
    return_3y: float | None = None
    return_5y: float | None = None
    volume: float | None = None
    volume_1m_avg: float | None = None
    high_price: float | None = None
    low_price: float | None = None
    all_time_high: float | None = None
    all_time_low: float | None = None
    dma_50: float | None = None
    dma_200: float | None = None
    rsi: float | None = None
    macd: float | None = None
    macd_signal: float | None = None
    previous_close: float | None = None
    free_cash_flow: float | None = None
    ev_ebitda: float | None = None
    peg_ratio: float | None = None
    intrinsic_value: float | None = None
    altman_z_score: float | None = None


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
    current_price: float | None = None
    market_cap: float | None = None
    pe_ratio: float | None = None
    price_to_book: float | None = None
    return_on_equity: float | None = None
    roce: float | None = None
    return_1y: float | None = None
    return_3m: float | None = None


class CompanyDetail(CompanySummary):
    metrics: list[MetricPoint]
    anomalies: list[dict] = []
