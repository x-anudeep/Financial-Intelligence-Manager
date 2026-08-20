import { Building2, Database, Upload } from "lucide-react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "../api/client";
import { KpiCard } from "../components/KpiCard";
import { money, percent } from "../utils/format";

export function PortfolioDashboard({ onSelectCompany }: { onSelectCompany: (id: number) => void }) {
  const queryClient = useQueryClient();
  const companies = useQuery({ queryKey: ["companies"], queryFn: api.companies });
  const seed = useMutation({ mutationFn: api.seed, onSuccess: () => queryClient.invalidateQueries({ queryKey: ["companies"] }) });
  const upload = useMutation({ mutationFn: api.uploadFinancials, onSuccess: () => queryClient.invalidateQueries({ queryKey: ["companies"] }) });
  const totalRevenue = companies.data?.reduce((sum, company) => sum + (company.latest_revenue ?? 0), 0) ?? 0;
  const totalDebt = companies.data?.reduce((sum, company) => sum + (company.latest_debt ?? 0), 0) ?? 0;
  const margin = companies.data?.filter((c) => c.ebitda_margin != null).reduce((sum, c) => sum + (c.ebitda_margin ?? 0), 0) ?? 0;
  const avgMargin = companies.data?.length ? margin / companies.data.length : null;

  return (
    <main className="mx-auto flex max-w-7xl flex-col gap-6 px-6 py-6">
      <div className="flex flex-wrap items-center justify-between gap-4 border-b border-line pb-5">
        <div>
          <h1 className="text-3xl font-semibold text-ink">Financial Intelligence Platform</h1>
          <p className="mt-1 text-sm text-slate-600">Deterministic statement analysis for middle-market company review.</p>
        </div>
        <div className="flex items-center gap-3">
          <label className="inline-flex cursor-pointer items-center gap-2 rounded-md border border-line bg-white px-3 py-2 text-sm font-medium shadow-sm">
            <Upload size={16} /> Upload CSV/XLSX
            <input className="hidden" type="file" accept=".csv,.xlsx" onChange={(event) => event.target.files?.[0] && upload.mutate(event.target.files[0])} />
          </label>
          <button onClick={() => seed.mutate()} className="inline-flex items-center gap-2 rounded-md bg-ink px-3 py-2 text-sm font-medium text-white shadow-sm">
            <Database size={16} /> Seed Demo Data
          </button>
        </div>
      </div>

      {(seed.error || upload.error) && <div className="rounded-md border border-red-200 bg-red-50 p-3 text-sm text-red-700">{(seed.error ?? upload.error)?.message}</div>}

      <div className="grid gap-4 md:grid-cols-4">
        <KpiCard label="Companies Analyzed" value={String(companies.data?.length ?? 0)} />
        <KpiCard label="Latest Revenue" value={money(totalRevenue)} />
        <KpiCard label="Latest Debt" value={money(totalDebt)} />
        <KpiCard label="Avg EBITDA Margin" value={percent(avgMargin)} />
      </div>

      <section className="overflow-hidden rounded-md border border-line bg-white shadow-sm">
        <div className="border-b border-line px-4 py-3 text-sm font-semibold uppercase tracking-wide text-slate-600">Recently Analyzed Companies</div>
        {companies.isLoading ? <div className="p-6 text-sm text-slate-500">Loading companies...</div> : null}
        {!companies.isLoading && !companies.data?.length ? <div className="p-6 text-sm text-slate-500">No companies loaded yet. Seed demo data or upload a financial file.</div> : null}
        <div className="divide-y divide-line">
          {companies.data?.map((company) => (
            <button key={company.id} onClick={() => onSelectCompany(company.id)} className="grid w-full grid-cols-1 gap-3 px-4 py-4 text-left hover:bg-slate-50 md:grid-cols-[2fr_1fr_1fr_1fr_1fr]">
              <div className="flex items-center gap-3">
                <Building2 className="text-slate-500" size={20} />
                <div>
                  <div className="font-semibold text-ink">{company.name}</div>
                  <div className="text-sm text-slate-500">{company.industry}</div>
                </div>
              </div>
              <Cell label="Period" value={company.latest_period ?? "N/A"} />
              <Cell label="Revenue" value={money(company.latest_revenue)} />
              <Cell label="EBITDA" value={money(company.latest_ebitda)} />
              <Cell label="Revenue Growth" value={percent(company.revenue_growth)} />
            </button>
          ))}
        </div>
      </section>
    </main>
  );
}

function Cell({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <div className="text-xs uppercase tracking-wide text-slate-400">{label}</div>
      <div className="mt-1 text-sm font-medium text-ink">{value}</div>
    </div>
  );
}
