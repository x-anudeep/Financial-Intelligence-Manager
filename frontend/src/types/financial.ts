export type MetricPoint = {
  [key: string]: string | number | null | undefined;
  period: string;
  fiscal_year: number;
  revenue?: number | null;
  ebitda?: number | null;
  net_income?: number | null;
  cash?: number | null;
  total_debt?: number | null;
  total_assets?: number | null;
  total_equity?: number | null;
  operating_cash_flow?: number | null;
  accounts_receivable?: number | null;
  current_assets?: number | null;
  current_liabilities?: number | null;
  revenue_growth?: number | null;
  ebitda_margin?: number | null;
  gross_margin?: number | null;
  current_ratio?: number | null;
  quick_ratio?: number | null;
  debt_to_ebitda?: number | null;
  working_capital?: number | null;
  current_price?: number | null;
  market_cap?: number | null;
  eps?: number | null;
  pe_ratio?: number | null;
  price_to_book?: number | null;
  price_to_sales?: number | null;
  dividend_yield?: number | null;
  return_on_equity?: number | null;
  return_on_assets?: number | null;
  roce?: number | null;
  debt_to_equity?: number | null;
  promoter_holding?: number | null;
  fii_holding?: number | null;
  dii_holding?: number | null;
  sales_growth_3y?: number | null;
  sales_growth_5y?: number | null;
  profit_growth_3y?: number | null;
  profit_growth_5y?: number | null;
  return_1d?: number | null;
  return_1w?: number | null;
  return_1m?: number | null;
  return_3m?: number | null;
  return_6m?: number | null;
  return_1y?: number | null;
  return_3y?: number | null;
  return_5y?: number | null;
  volume?: number | null;
  volume_1m_avg?: number | null;
  high_price?: number | null;
  low_price?: number | null;
  all_time_high?: number | null;
  all_time_low?: number | null;
  dma_50?: number | null;
  dma_200?: number | null;
  rsi?: number | null;
  macd?: number | null;
  macd_signal?: number | null;
  previous_close?: number | null;
  free_cash_flow?: number | null;
  ev_ebitda?: number | null;
  peg_ratio?: number | null;
  intrinsic_value?: number | null;
  altman_z_score?: number | null;
  interest_income?: number | null;
  interest_expense?: number | null;
  net_interest_income?: number | null;
  noninterest_income?: number | null;
  noninterest_expense?: number | null;
  loan_loss_provision?: number | null;
  deposits?: number | null;
  loans?: number | null;
  investment_securities?: number | null;
  loan_to_deposit?: number | null;
  efficiency_ratio?: number | null;
  provision_to_loans?: number | null;
  deposit_growth?: number | null;
  loan_growth?: number | null;
  net_income_growth?: number | null;
};

export type CompanySummary = {
  id: number;
  name: string;
  industry: string;
  description?: string | null;
  latest_period?: string | null;
  latest_revenue?: number | null;
  latest_ebitda?: number | null;
  latest_cash?: number | null;
  latest_debt?: number | null;
  revenue_growth?: number | null;
  ebitda_margin?: number | null;
  current_price?: number | null;
  market_cap?: number | null;
  pe_ratio?: number | null;
  price_to_book?: number | null;
  return_on_equity?: number | null;
  roce?: number | null;
  return_1y?: number | null;
  return_3m?: number | null;
};

export type CompanyDetail = CompanySummary & {
  metrics: MetricPoint[];
  anomalies: Anomaly[];
};

export type Anomaly = {
  id: number;
  company_id: number;
  company_name?: string | null;
  period: string;
  anomaly_type: string;
  metric: string;
  severity: "low" | "medium" | "high" | "critical" | string;
  title: string;
  description: string;
  current_value?: number | null;
  previous_value?: number | null;
  percentage_change?: number | null;
  evidence: string;
  suggested_review: string;
  anomaly_score?: number | null;
  method: string;
  supporting_statistics?: string | null;
};

export type PortfolioRisk = {
  total_companies: number;
  total_anomalies: number;
  high_risk_exceptions: number;
  critical_exceptions: number;
  severity_distribution: Record<string, number>;
  anomaly_categories: Record<string, number>;
  companies_requiring_review: Array<{ company_id: number; company_name: string; risk_score: number; exception_count: number }>;
};

export type ComparisonRow = {
  company_id: number;
  name: string;
  industry: string;
  revenue_growth?: number | null;
  ebitda_margin?: number | null;
  debt_to_ebitda?: number | null;
  operating_cash_conversion?: number | null;
  current_ratio?: number | null;
  working_capital_growth?: number | null;
  exception_count: number;
  latest_revenue?: number | null;
};

export type RetrievedContext = {
  document_id: number;
  document_name: string;
  chunk_id: number;
  content: string;
  score: number;
  page?: string | null;
  section?: string | null;
};

export type AnalystAnswer = {
  answer: string;
  ai_enabled: boolean;
  structured_findings: Array<Record<string, unknown>>;
  sources: RetrievedContext[];
};

export type DocumentRecord = {
  id: number;
  company_id: number;
  file_name: string;
  document_type: string;
  processing_status: string;
};
