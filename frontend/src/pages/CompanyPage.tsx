import { ArrowLeft } from "lucide-react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { api } from "../api/client";
import { BankBalanceSheetChart, BankIncomeChart, CashDebtChart, MarginChart, RevenueEbitdaChart } from "../charts/FinancialCharts";
import { AnalystCopilot } from "../components/AnalystCopilot";
import { DocumentPanel } from "../components/DocumentPanel";
import { KpiCard } from "../components/KpiCard";
import { SeverityBadge } from "../components/SeverityBadge";
import { SourceList } from "../components/SourceList";
import { compact, crore, money, number, percent, rupee } from "../utils/format";

export function CompanyPage({ companyId, onBack }: { companyId: number; onBack: () => void }) {
  const company = useQuery({ queryKey: ["company", companyId], queryFn: () => api.company(companyId) });
  const supportingContext = useMutation({ mutationFn: (anomalyId: number) => api.supportingContext(anomalyId) });
  const latest = company.data?.metrics.at(-1);

  if (company.isLoading) return <main className="p-6 text-sm text-slate-400">Loading company financials...</main>;
  if (company.error) return <main className="p-6 text-sm text-red-700">{company.error.message}</main>;
  if (!company.data) return null;
  const isArchiveData = latest?.market_cap != null;
  const isBankData = !isArchiveData && (latest?.deposits != null || latest?.loans != null || latest?.net_interest_income != null);
  const visibleMetricKeys = latest ? Object.keys(latest).filter((key) => !HIDDEN_METRIC_KEYS.has(key) && latest[key] != null).sort() : [];

  return (
    <main className="mx-auto flex max-w-7xl flex-col gap-6 px-6 py-6">
      <div className="flex items-center justify-between border-b border-slate-800 pb-5">
        <div>
          <button onClick={onBack} className="mb-3 inline-flex items-center gap-2 text-sm font-medium text-slate-300 hover:text-slate-100">
            <ArrowLeft size={16} /> Portfolio
          </button>
          <h1 className="text-3xl font-semibold text-slate-100">{company.data.name}</h1>
          <p className="mt-1 text-sm text-slate-300">{company.data.industry} | Latest period {company.data.latest_period ?? "N/A"} | {company.data.anomalies.length} exceptions</p>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-4 lg:grid-cols-7">
        {isArchiveData ? (
          <>
            <KpiCard label="Price" value={rupee(latest?.current_price)} sublabel={`Prev ${rupee(latest?.previous_close)}`} />
            <KpiCard label="Market Cap" value={crore(latest?.market_cap)} />
            <KpiCard label="PE" value={number(latest?.pe_ratio)} />
            <KpiCard label="Price / Book" value={number(latest?.price_to_book)} />
            <KpiCard label="ROE" value={percent(latest?.return_on_equity)} />
            <KpiCard label="ROCE" value={percent(latest?.roce)} />
            <KpiCard label="1Y Return" value={percent(latest?.return_1y)} />
          </>
        ) : isBankData ? (
          <>
            <KpiCard label="Revenue" value={money(latest?.revenue)} sublabel={percent(latest?.revenue_growth)} />
            <KpiCard label="Net Income" value={money(latest?.net_income)} sublabel={percent(latest?.net_income_growth)} />
            <KpiCard label="Deposits" value={money(latest?.deposits)} sublabel={percent(latest?.deposit_growth)} />
            <KpiCard label="Loans" value={money(latest?.loans)} sublabel={percent(latest?.loan_growth)} />
            <KpiCard label="Total Assets" value={money(latest?.total_assets)} />
            <KpiCard label="ROA" value={percent(latest?.return_on_assets)} />
            <KpiCard label="ROE" value={percent(latest?.return_on_equity)} />
          </>
        ) : (
          <>
            <KpiCard label="Revenue" value={money(latest?.revenue)} sublabel={percent(latest?.revenue_growth)} />
            <KpiCard label="EBITDA" value={money(latest?.ebitda)} />
            <KpiCard label="EBITDA Margin" value={percent(latest?.ebitda_margin)} />
            <KpiCard label="Cash" value={money(latest?.cash)} />
            <KpiCard label="Debt" value={money(latest?.total_debt)} />
            <KpiCard label="Debt / EBITDA" value={number(latest?.debt_to_ebitda)} />
            <KpiCard label="Current Ratio" value={number(latest?.current_ratio)} />
          </>
        )}
      </div>

      {isArchiveData ? (
        <section className="rounded-md border border-slate-800 bg-slate-900/80 p-4 shadow-sm shadow-black/20">
          <h3 className="mb-4 text-sm font-semibold uppercase tracking-wide text-slate-300">Market Snapshot</h3>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <Metric label="Sales" value={crore(latest?.revenue)} />
            <Metric label="Net Profit" value={crore(latest?.net_income)} />
            <Metric label="EPS" value={number(latest?.eps)} />
            <Metric label="Dividend Yield" value={percent(latest?.dividend_yield)} />
            <Metric label="Debt / Equity" value={number(latest?.debt_to_equity)} />
            <Metric label="Current Ratio" value={number(latest?.current_ratio)} />
            <Metric label="Free Cash Flow" value={crore(latest?.free_cash_flow)} />
            <Metric label="Altman Z" value={number(latest?.altman_z_score)} />
            <Metric label="3Y Sales Growth" value={percent(latest?.sales_growth_3y)} />
            <Metric label="3Y Profit Growth" value={percent(latest?.profit_growth_3y)} />
            <Metric label="3M Return" value={percent(latest?.return_3m)} />
            <Metric label="6M Return" value={percent(latest?.return_6m)} />
            <Metric label="RSI" value={number(latest?.rsi)} />
            <Metric label="50 DMA" value={rupee(latest?.dma_50)} />
            <Metric label="200 DMA" value={rupee(latest?.dma_200)} />
            <Metric label="Volume" value={compact(latest?.volume)} />
            <Metric label="Promoter Holding" value={percent(latest?.promoter_holding)} />
            <Metric label="FII Holding" value={percent(latest?.fii_holding)} />
            <Metric label="DII Holding" value={percent(latest?.dii_holding)} />
            <Metric label="Intrinsic Value" value={rupee(latest?.intrinsic_value)} />
          </div>
        </section>
      ) : null}

      {isBankData ? (
        <section className="rounded-md border border-slate-800 bg-slate-900/80 p-4 shadow-sm shadow-black/20">
          <h3 className="mb-4 text-sm font-semibold uppercase tracking-wide text-slate-300">Bank Operating Snapshot</h3>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            {bankSnapshotMetrics(latest).map((metric) => (
              <Metric key={metric.label} label={metric.label} value={metric.value} />
            ))}
          </div>
        </section>
      ) : null}

      <div className="grid gap-4 lg:grid-cols-2">
        {isBankData ? (
          <>
            <BankIncomeChart data={company.data.metrics} />
            <BankBalanceSheetChart data={company.data.metrics} />
          </>
        ) : (
          <>
            <RevenueEbitdaChart data={company.data.metrics} />
            <CashDebtChart data={company.data.metrics} />
            <MarginChart data={company.data.metrics} />
          </>
        )}
        <section className="rounded-md border border-slate-800 bg-slate-900/80 p-4 shadow-sm shadow-black/20">
          <h3 className="mb-4 text-sm font-semibold uppercase tracking-wide text-slate-300">{isBankData ? "Bank Financial History" : "Financial History"}</h3>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              {isBankData ? (
                <thead className="text-left text-xs uppercase tracking-wide text-slate-400">
                  <tr>
                    <th className="py-2">Period</th>
                    <th>Revenue</th>
                    <th>Net Income</th>
                    <th>Deposits</th>
                    <th>Loans</th>
                    <th>Efficiency</th>
                    <th>Loan / Deposit</th>
                  </tr>
                </thead>
              ) : (
                <thead className="text-left text-xs uppercase tracking-wide text-slate-400">
                  <tr>
                    <th className="py-2">Period</th>
                    <th>Revenue</th>
                    <th>EBITDA Margin</th>
                    <th>Cash</th>
                    <th>Debt</th>
                    <th>Working Capital</th>
                  </tr>
                </thead>
              )}
              <tbody className="divide-y divide-slate-800">
                {company.data.metrics.map((row) => (
                  <tr key={row.period}>
                    <td className="py-2 font-medium">{row.period}</td>
                    {isBankData ? (
                      <>
                        <td>{money(row.revenue)}</td>
                        <td>{money(row.net_income)}</td>
                        <td>{money(row.deposits)}</td>
                        <td>{money(row.loans)}</td>
                        <td>{percent(row.efficiency_ratio)}</td>
                        <td>{number(row.loan_to_deposit)}</td>
                      </>
                    ) : (
                      <>
                        <td>{money(row.revenue)}</td>
                        <td>{percent(row.ebitda_margin)}</td>
                        <td>{money(row.cash)}</td>
                        <td>{money(row.total_debt)}</td>
                        <td>{money(row.working_capital)}</td>
                      </>
                    )}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      </div>

      {visibleMetricKeys.length ? (
        <section className="rounded-md border border-slate-800 bg-slate-900/80 p-4 shadow-sm shadow-black/20">
          <h3 className="mb-4 text-sm font-semibold uppercase tracking-wide text-slate-300">All Uploaded Metrics</h3>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            {visibleMetricKeys.map((key) => (
              <Metric key={key} label={labelize(key)} value={formatGeneric(latest?.[key])} />
            ))}
          </div>
        </section>
      ) : null}

      <div className="grid gap-4 lg:grid-cols-2">
        <DocumentPanel companyId={companyId} />
        <AnalystCopilot companyId={companyId} />
      </div>

      <section className="rounded-md border border-slate-800 bg-slate-900/80 shadow-sm shadow-black/20">
        <div className="border-b border-slate-800 px-4 py-3 text-sm font-semibold uppercase tracking-wide text-slate-300">Risk / Anomaly Timeline</div>
        <div className="divide-y divide-slate-800">
          {company.data.anomalies.map((item) => (
            <div key={item.id} className="grid gap-3 px-4 py-4 lg:grid-cols-[120px_1fr_2fr_1.2fr_180px]">
              <SeverityBadge severity={item.severity} />
              <div>
                <div className="font-semibold text-slate-100">{item.title}</div>
                <div className="text-sm text-slate-400">{item.period} | {item.metric} | {item.method}</div>
              </div>
              <div className="text-sm text-slate-300">{item.evidence}</div>
              <div className="whitespace-pre-line text-sm text-slate-300">{item.suggested_review}</div>
              <button onClick={() => supportingContext.mutate(item.id)} className="h-9 rounded-md border border-slate-800 px-3 text-sm font-medium hover:bg-slate-950/40">Find Context</button>
            </div>
          ))}
          {!company.data.anomalies.length ? <div className="p-5 text-sm text-slate-400">No exceptions currently detected for this company.</div> : null}
        </div>
      </section>

      {supportingContext.data ? (
        <section className="rounded-md border border-slate-800 bg-slate-900/80 p-4 shadow-sm shadow-black/20">
          <h3 className="mb-3 text-sm font-semibold uppercase tracking-wide text-slate-300">Structured Finding + Document Context</h3>
          <div className="mb-4 rounded-md bg-slate-950/40 p-3 text-sm text-slate-300">{supportingContext.data.answer}</div>
          <SourceList sources={supportingContext.data.sources} />
        </section>
      ) : null}
    </main>
  );
}

const HIDDEN_METRIC_KEYS = new Set([
  "period",
  "fiscal_year",
  "revenue",
  "gross_profit",
  "ebitda",
  "net_income",
  "cash",
  "accounts_receivable",
  "inventory",
  "accounts_payable",
  "current_assets",
  "current_liabilities",
  "total_debt",
  "operating_cash_flow",
  "gross_margin",
  "ebitda_margin",
  "net_margin",
  "current_ratio",
  "quick_ratio",
  "debt_to_ebitda",
  "operating_cash_flow_to_ebitda",
  "revenue_growth",
  "ebitda_growth",
  "cash_change",
  "debt_growth",
  "working_capital",
  "working_capital_growth",
  "interest_income",
  "net_interest_income",
  "noninterest_income",
  "noninterest_expense",
  "loan_loss_provision",
  "deposits",
  "loans",
  "investment_securities",
  "loan_to_deposit",
  "efficiency_ratio",
  "provision_to_loans",
  "return_on_assets",
  "return_on_equity",
  "deposit_growth",
  "loan_growth",
  "net_income_growth",
]);

function labelize(key: string) {
  return key.replace(/_/g, " ").replace(/\b\w/g, (char) => char.toUpperCase());
}

function formatGeneric(value: string | number | null | undefined) {
  if (value == null) return "N/A";
  if (typeof value === "string") return value;
  return new Intl.NumberFormat("en-IN", { maximumFractionDigits: 2 }).format(value);
}

function bankSnapshotMetrics(latest: Record<string, string | number | null | undefined> | undefined) {
  const items = [
    ["Interest Income", moneyValue(latest?.interest_income)],
    ["Interest Expense", moneyValue(latest?.interest_expense)],
    ["Net Interest Income", moneyValue(latest?.net_interest_income)],
    ["Noninterest Income", moneyValue(latest?.noninterest_income)],
    ["Noninterest Expense", moneyValue(latest?.noninterest_expense)],
    ["Loan Loss Provision", moneyValue(latest?.loan_loss_provision)],
    ["Investment Securities", moneyValue(latest?.investment_securities)],
    ["Provision / Loans", percentValue(latest?.provision_to_loans)],
    ["Efficiency Ratio", percentValue(latest?.efficiency_ratio)],
    ["Loan / Deposit", numberValue(latest?.loan_to_deposit)],
    ["Total Equity", moneyValue(latest?.total_equity)],
    ["EPS", numberValue(latest?.eps)],
  ];
  return items.filter(([, value]) => value !== "N/A").map(([label, value]) => ({ label, value }));
}

function numberFromMetric(value: string | number | null | undefined) {
  return typeof value === "number" ? value : null;
}

function moneyValue(value: string | number | null | undefined) {
  return money(numberFromMetric(value));
}

function percentValue(value: string | number | null | undefined) {
  return percent(numberFromMetric(value));
}

function numberValue(value: string | number | null | undefined) {
  return number(numberFromMetric(value));
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="border-b border-slate-800 pb-3">
      <div className="text-xs uppercase tracking-wide text-slate-400">{label}</div>
      <div className="mt-1 text-sm font-semibold text-slate-100">{value}</div>
    </div>
  );
}
