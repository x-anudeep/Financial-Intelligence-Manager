export type MetricPoint = {
  period: string;
  fiscal_year: number;
  revenue?: number | null;
  ebitda?: number | null;
  cash?: number | null;
  total_debt?: number | null;
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
