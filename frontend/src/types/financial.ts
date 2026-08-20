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
};
