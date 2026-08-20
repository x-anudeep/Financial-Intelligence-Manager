import { Filter } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import { useMemo, useState } from "react";
import { api } from "../api/client";
import { SeverityBadge } from "../components/SeverityBadge";
import { money, percent } from "../utils/format";

export function ExceptionCenter({ onOpenCompany }: { onOpenCompany: (id: number) => void }) {
  const [severity, setSeverity] = useState("");
  const [type, setType] = useState("");
  const params = useMemo(() => {
    const search = new URLSearchParams();
    if (severity) search.set("severity", severity);
    if (type) search.set("anomaly_type", type);
    const value = search.toString();
    return value ? `?${value}` : "";
  }, [severity, type]);
  const anomalies = useQuery({ queryKey: ["anomalies", params], queryFn: () => api.anomalies(params) });
  const types = Array.from(new Set(anomalies.data?.map((item) => item.anomaly_type) ?? []));

  return (
    <section className="rounded-md border border-line bg-white shadow-sm">
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-line px-4 py-3">
        <div className="flex items-center gap-2 text-sm font-semibold uppercase tracking-wide text-slate-600">
          <Filter size={16} /> Exception Center
        </div>
        <div className="flex gap-2">
          <select value={severity} onChange={(event) => setSeverity(event.target.value)} className="rounded-md border border-line bg-white px-2 py-1 text-sm">
            <option value="">All severities</option>
            <option value="critical">Critical</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>
          <select value={type} onChange={(event) => setType(event.target.value)} className="rounded-md border border-line bg-white px-2 py-1 text-sm">
            <option value="">All types</option>
            {types.map((item) => <option key={item} value={item}>{item}</option>)}
          </select>
        </div>
      </div>
      <div className="divide-y divide-line">
        {anomalies.data?.slice(0, 20).map((item) => (
          <button key={item.id} onClick={() => onOpenCompany(item.company_id)} className="grid w-full gap-3 px-4 py-4 text-left hover:bg-slate-50 lg:grid-cols-[130px_1.2fr_1fr_2fr]">
            <SeverityBadge severity={item.severity} />
            <div>
              <div className="font-semibold text-ink">{item.title}</div>
              <div className="text-sm text-slate-500">{item.company_name} | {item.period} | {item.metric}</div>
            </div>
            <div className="text-sm">
              <div>{money(item.current_value)}</div>
              <div className="text-slate-500">{percent(item.percentage_change)}</div>
            </div>
            <div className="text-sm text-slate-600">{item.evidence}</div>
          </button>
        ))}
        {!anomalies.isLoading && !anomalies.data?.length ? <div className="p-5 text-sm text-slate-500">No exceptions match the selected filters.</div> : null}
      </div>
    </section>
  );
}
