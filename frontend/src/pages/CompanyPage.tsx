import { ArrowLeft } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import { api } from "../api/client";
import { CashDebtChart, MarginChart, RevenueEbitdaChart } from "../charts/FinancialCharts";
import { KpiCard } from "../components/KpiCard";
import { SeverityBadge } from "../components/SeverityBadge";
import { money, number, percent } from "../utils/format";

export function CompanyPage({ companyId, onBack }: { companyId: number; onBack: () => void }) {
  const company = useQuery({ queryKey: ["company", companyId], queryFn: () => api.company(companyId) });
  const latest = company.data?.metrics.at(-1);

  if (company.isLoading) return <main className="p-6 text-sm text-slate-500">Loading company financials...</main>;
  if (company.error) return <main className="p-6 text-sm text-red-700">{company.error.message}</main>;
  if (!company.data) return null;

  return (
    <main className="mx-auto flex max-w-7xl flex-col gap-6 px-6 py-6">
      <div className="flex items-center justify-between border-b border-line pb-5">
        <div>
          <button onClick={onBack} className="mb-3 inline-flex items-center gap-2 text-sm font-medium text-slate-600 hover:text-ink">
            <ArrowLeft size={16} /> Portfolio
          </button>
          <h1 className="text-3xl font-semibold text-ink">{company.data.name}</h1>
          <p className="mt-1 text-sm text-slate-600">{company.data.industry} · Latest period {company.data.latest_period ?? "N/A"} · {company.data.anomalies.length} exceptions</p>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-4 lg:grid-cols-7">
        <KpiCard label="Revenue" value={money(latest?.revenue)} sublabel={percent(latest?.revenue_growth)} />
        <KpiCard label="EBITDA" value={money(latest?.ebitda)} />
        <KpiCard label="EBITDA Margin" value={percent(latest?.ebitda_margin)} />
        <KpiCard label="Cash" value={money(latest?.cash)} />
        <KpiCard label="Debt" value={money(latest?.total_debt)} />
        <KpiCard label="Debt / EBITDA" value={number(latest?.debt_to_ebitda)} />
        <KpiCard label="Current Ratio" value={number(latest?.current_ratio)} />
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <RevenueEbitdaChart data={company.data.metrics} />
        <CashDebtChart data={company.data.metrics} />
        <MarginChart data={company.data.metrics} />
        <section className="rounded-md border border-line bg-white p-4 shadow-sm">
          <h3 className="mb-4 text-sm font-semibold uppercase tracking-wide text-slate-600">Financial History</h3>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="text-left text-xs uppercase tracking-wide text-slate-500">
                <tr>
                  <th className="py-2">Period</th>
                  <th>Revenue</th>
                  <th>EBITDA Margin</th>
                  <th>Cash</th>
                  <th>Debt</th>
                  <th>Working Capital</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-line">
                {company.data.metrics.map((row) => (
                  <tr key={row.period}>
                    <td className="py-2 font-medium">{row.period}</td>
                    <td>{money(row.revenue)}</td>
                    <td>{percent(row.ebitda_margin)}</td>
                    <td>{money(row.cash)}</td>
                    <td>{money(row.total_debt)}</td>
                    <td>{money(row.working_capital)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      </div>

      <section className="rounded-md border border-line bg-white shadow-sm">
        <div className="border-b border-line px-4 py-3 text-sm font-semibold uppercase tracking-wide text-slate-600">Risk / Anomaly Timeline</div>
        <div className="divide-y divide-line">
          {company.data.anomalies.map((item) => (
            <div key={item.id} className="grid gap-3 px-4 py-4 lg:grid-cols-[120px_1fr_2fr_1.2fr]">
              <SeverityBadge severity={item.severity} />
              <div>
                <div className="font-semibold text-ink">{item.title}</div>
                <div className="text-sm text-slate-500">{item.period} · {item.metric} · {item.method}</div>
              </div>
              <div className="text-sm text-slate-600">{item.evidence}</div>
              <div className="whitespace-pre-line text-sm text-slate-600">{item.suggested_review}</div>
            </div>
          ))}
          {!company.data.anomalies.length ? <div className="p-5 text-sm text-slate-500">No exceptions currently detected for this company.</div> : null}
        </div>
      </section>
    </main>
  );
}
