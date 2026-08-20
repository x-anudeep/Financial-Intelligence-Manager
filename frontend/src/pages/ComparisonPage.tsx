import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { api } from "../api/client";
import { LeverageMarginScatter } from "../charts/RiskCharts";
import { money, number, percent } from "../utils/format";

export function ComparisonPage() {
  const companies = useQuery({ queryKey: ["companies"], queryFn: api.companies });
  const [selected, setSelected] = useState<number[]>([]);
  const comparison = useQuery({ queryKey: ["comparison", selected], queryFn: () => api.compare(selected), enabled: selected.length >= 2 });

  function toggle(id: number) {
    setSelected((current) => current.includes(id) ? current.filter((item) => item !== id) : current.length < 5 ? [...current, id] : current);
  }

  return (
    <section className="rounded-md border border-slate-800 bg-slate-900/80 p-4 shadow-sm shadow-black/20">
      <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
        <h3 className="text-sm font-semibold uppercase tracking-wide text-slate-300">Company Comparison</h3>
        <div className="flex flex-wrap gap-2">
          {companies.data?.slice(0, 12).map((company) => (
            <label key={company.id} className="inline-flex items-center gap-2 rounded-md border border-slate-800 bg-slate-950/30 px-2 py-1 text-sm text-slate-300">
              <input type="checkbox" checked={selected.includes(company.id)} onChange={() => toggle(company.id)} />
              {company.name}
            </label>
          ))}
        </div>
      </div>
      {comparison.data ? (
        <div className="grid gap-4 lg:grid-cols-2">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="text-left text-xs uppercase tracking-wide text-slate-400">
                <tr><th className="py-2">Company</th><th>Revenue Growth</th><th>EBITDA Margin</th><th>Debt / EBITDA</th><th>Cash Conversion</th><th>Exceptions</th></tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {comparison.data.companies.map((row) => (
                  <tr key={row.company_id}>
                    <td className="py-2 font-medium">{row.name}<div className="text-xs text-slate-400">{money(row.latest_revenue)}</div></td>
                    <td>{percent(row.revenue_growth)}</td>
                    <td>{percent(row.ebitda_margin)}</td>
                    <td>{number(row.debt_to_ebitda)}</td>
                    <td>{percent(row.operating_cash_conversion)}</td>
                    <td>{row.exception_count}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <LeverageMarginScatter data={comparison.data.companies} />
        </div>
      ) : <div className="text-sm text-slate-400">Select 2 to 5 companies to compare.</div>}
    </section>
  );
}
