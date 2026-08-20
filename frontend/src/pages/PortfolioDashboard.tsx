import { Building2, Bot, FileSpreadsheet, Search, Upload } from "lucide-react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useMemo, useState } from "react";
import { api } from "../api/client";
import { CategoryDistribution, SeverityDistribution } from "../charts/RiskCharts";
import { KpiCard } from "../components/KpiCard";
import { ComparisonPage } from "./ComparisonPage";
import { ExceptionCenter } from "./ExceptionCenter";
import { crore, money, percent, rupee } from "../utils/format";

export function PortfolioDashboard({ onSelectCompany }: { onSelectCompany: (id: number) => void }) {
  const queryClient = useQueryClient();
  const companies = useQuery({ queryKey: ["companies"], queryFn: api.companies });
  const risk = useQuery({ queryKey: ["portfolio-risk"], queryFn: api.portfolioRisk });
  const upload = useMutation({ mutationFn: api.uploadFinancials, onSuccess: () => queryClient.invalidateQueries() });
  const fetchSec = useMutation({ mutationFn: api.fetchSecFinancials, onSuccess: () => queryClient.invalidateQueries() });
  const [search, setSearch] = useState("");
  const [agentQuery, setAgentQuery] = useState("");
  const [sortBy, setSortBy] = useState<"name" | "market_cap" | "revenue" | "return_1y">("market_cap");
  const totalRevenue = companies.data?.reduce((sum, company) => sum + (company.latest_revenue ?? 0), 0) ?? 0;
  const totalDebt = companies.data?.reduce((sum, company) => sum + (company.latest_debt ?? 0), 0) ?? 0;
  const margin = companies.data?.filter((c) => c.ebitda_margin != null).reduce((sum, c) => sum + (c.ebitda_margin ?? 0), 0) ?? 0;
  const avgMargin = companies.data?.length ? margin / companies.data.length : null;
  const archiveCompanies = companies.data?.filter((company) => company.market_cap != null) ?? [];
  const isArchiveData = archiveCompanies.length > 0;
  const totalMarketCap = archiveCompanies.reduce((sum, company) => sum + (company.market_cap ?? 0), 0);
  const average = (values: Array<number | null | undefined>) => {
    const present = values.filter((value): value is number => value != null);
    return present.length ? present.reduce((sum, value) => sum + value, 0) / present.length : null;
  };
  const avgPe = average(archiveCompanies.map((company) => company.pe_ratio));
  const avgRoe = average(archiveCompanies.map((company) => company.return_on_equity));
  const avgOneYearReturn = average(archiveCompanies.map((company) => company.return_1y));
  const avgThreeMonthReturn = average(archiveCompanies.map((company) => company.return_3m));
  const hasCompanies = Boolean(companies.data?.length);
  const filteredCompanies = useMemo(() => {
    const term = search.trim().toLowerCase();
    return [...(companies.data ?? [])]
      .filter((company) => !term || `${company.name} ${company.industry}`.toLowerCase().includes(term))
      .sort((a, b) => {
        if (sortBy === "name") return a.name.localeCompare(b.name);
        if (sortBy === "market_cap") return (b.market_cap ?? 0) - (a.market_cap ?? 0);
        if (sortBy === "return_1y") return (b.return_1y ?? -Infinity) - (a.return_1y ?? -Infinity);
        return (b.latest_revenue ?? 0) - (a.latest_revenue ?? 0);
      });
  }, [companies.data, search, sortBy]);

  return (
    <main className="mx-auto flex max-w-7xl flex-col gap-6 px-6 py-6">
      <div className="flex flex-wrap items-center justify-between gap-4 border-b border-slate-800 pb-5">
        <div>
          <h1 className="text-3xl font-semibold text-slate-100">Financial Intelligence Platform</h1>
          <p className="mt-1 text-sm text-slate-400">Upload financial data, review exceptions, and connect supporting documents to analyst questions.</p>
        </div>
        <div className="flex items-center gap-3">
          <label className="inline-flex cursor-pointer items-center gap-2 rounded-md border border-sky-400/40 bg-sky-500 px-4 py-2 text-sm font-semibold text-slate-950 shadow-sm shadow-sky-950/30 hover:bg-sky-400">
            <Upload size={16} /> Upload Financial CSV/XLSX
            <input className="hidden" type="file" accept=".csv,.xlsx" onChange={(event) => event.target.files?.[0] && upload.mutate(event.target.files[0])} />
          </label>
        </div>
      </div>

      {upload.isPending ? <div className="rounded-md border border-sky-500/30 bg-sky-500/10 p-3 text-sm text-sky-200">Uploading and analyzing financial data...</div> : null}
      {upload.error ? <div className="rounded-md border border-red-500/40 bg-red-500/10 p-3 text-sm text-red-200">{upload.error.message}</div> : null}
      {fetchSec.error ? <div className="rounded-md border border-red-500/40 bg-red-500/10 p-3 text-sm text-red-200">{fetchSec.error.message}</div> : null}

      <section className="rounded-md border border-slate-800 bg-slate-900/80 p-4 shadow-sm shadow-black/20">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <div className="inline-flex items-center gap-2 text-sm font-semibold uppercase tracking-wide text-sky-300">
              <Bot size={16} /> Real Data Agent
            </div>
            <p className="mt-1 text-sm text-slate-400">Type a US public company ticker or name. The agent fetches real SEC EDGAR facts, creates a CSV, ingests it, and refreshes the dashboard.</p>
          </div>
          <form
            className="flex min-w-0 flex-1 gap-2 lg:max-w-xl"
            onSubmit={(event) => {
              event.preventDefault();
              if (agentQuery.trim()) fetchSec.mutate(agentQuery.trim());
            }}
          >
            <input value={agentQuery} onChange={(event) => setAgentQuery(event.target.value)} placeholder="AAPL, JPM, Microsoft, Tesla..." className="min-w-0 flex-1 rounded-md border border-slate-800 bg-slate-950/40 px-3 py-2 text-sm text-slate-100 outline-none placeholder:text-slate-500" />
            <button disabled={fetchSec.isPending} className="inline-flex items-center gap-2 rounded-md bg-sky-500 px-4 py-2 text-sm font-semibold text-slate-950 hover:bg-sky-400 disabled:cursor-not-allowed disabled:opacity-60">
              <Search size={16} /> {fetchSec.isPending ? "Fetching..." : "Fetch"}
            </button>
          </form>
        </div>
        {fetchSec.data ? <div className="mt-3 rounded-md border border-emerald-500/30 bg-emerald-500/10 p-3 text-sm text-emerald-200">Loaded {fetchSec.data.company} ({fetchSec.data.ticker}) from {fetchSec.data.source}. CSV saved at {fetchSec.data.csv_path}.</div> : null}
      </section>

      {!hasCompanies && !companies.isLoading ? (
        <section className="rounded-md border border-slate-800 bg-slate-900/80 p-8 shadow-sm shadow-black/20">
          <div className="flex flex-col gap-5 md:flex-row md:items-center md:justify-between">
            <div className="max-w-2xl">
              <div className="mb-4 inline-flex h-12 w-12 items-center justify-center rounded-md border border-sky-400/30 bg-sky-400/10 text-sky-300">
                <FileSpreadsheet size={24} />
              </div>
              <h2 className="text-2xl font-semibold text-slate-100">Start by uploading financial data</h2>
              <p className="mt-2 text-sm leading-6 text-slate-400">
                Use the generated large-company CSV or any CSV/XLSX with company names and numeric financial metrics. Once uploaded, this dashboard will show KPIs, exceptions, comparison tools, and company-level document support.
              </p>
            </div>
            <label className="inline-flex cursor-pointer items-center justify-center gap-2 rounded-md border border-sky-400/40 bg-sky-500 px-4 py-3 text-sm font-semibold text-slate-950 shadow-sm shadow-sky-950/30 hover:bg-sky-400">
              <Upload size={16} /> Choose CSV/XLSX
              <input className="hidden" type="file" accept=".csv,.xlsx" onChange={(event) => event.target.files?.[0] && upload.mutate(event.target.files[0])} />
            </label>
          </div>
        </section>
      ) : null}

      {hasCompanies ? (
        <>
          <div className="grid gap-4 md:grid-cols-4">
            <KpiCard label="Companies Analyzed" value={String(risk.data?.total_companies ?? companies.data?.length ?? 0)} />
            <KpiCard label={isArchiveData ? "Market Cap" : "Total Exceptions"} value={isArchiveData ? crore(totalMarketCap) : String(risk.data?.total_anomalies ?? 0)} />
            <KpiCard label={isArchiveData ? "Average PE" : "Critical Exceptions"} value={isArchiveData ? (avgPe == null ? "N/A" : avgPe.toFixed(1)) : String(risk.data?.critical_exceptions ?? 0)} />
            <KpiCard label={isArchiveData ? "Average 1Y Return" : "High-Risk Exceptions"} value={isArchiveData ? percent(avgOneYearReturn) : String(risk.data?.high_risk_exceptions ?? 0)} />
          </div>

          <div className="grid gap-4 lg:grid-cols-2">
            <SeverityDistribution risk={risk.data} />
            <CategoryDistribution risk={risk.data} />
          </div>

          <section className="rounded-md border border-slate-800 bg-slate-900/80 p-4 shadow-sm shadow-black/20">
            <h3 className="mb-4 text-sm font-semibold uppercase tracking-wide text-slate-300">Companies Requiring Review</h3>
            <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-5">
              {risk.data?.companies_requiring_review.map((item) => (
                <button key={item.company_id} onClick={() => onSelectCompany(item.company_id)} className="rounded-md border border-slate-800 bg-slate-950/30 p-3 text-left hover:bg-slate-800/70">
                  <div className="font-semibold text-slate-100">{item.company_name}</div>
                  <div className="mt-1 text-sm text-slate-400">{item.exception_count} exceptions | score {item.risk_score}</div>
                </button>
              ))}
              {!risk.data?.companies_requiring_review.length ? <div className="text-sm text-slate-400">No companies currently require review.</div> : null}
            </div>
          </section>

          <div className="grid gap-4 md:grid-cols-3">
            <KpiCard label={isArchiveData ? "Average ROE" : "Latest Revenue"} value={isArchiveData ? percent(avgRoe) : money(totalRevenue)} />
            <KpiCard label={isArchiveData ? "3M Momentum" : "Latest Debt"} value={isArchiveData ? percent(avgThreeMonthReturn) : money(totalDebt)} />
            <KpiCard label="Avg EBITDA Margin" value={percent(avgMargin)} />
          </div>
        </>
      ) : null}

      <section className="overflow-hidden rounded-md border border-slate-800 bg-slate-900/80 shadow-sm shadow-black/20">
        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-800 px-4 py-3">
          <div className="text-sm font-semibold uppercase tracking-wide text-slate-300">Companies</div>
          <div className="flex flex-wrap items-center gap-2">
            <label className="inline-flex items-center gap-2 rounded-md border border-slate-800 bg-slate-950/40 px-3 py-2 text-sm text-slate-300">
              <Search size={16} />
              <input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Search company or industry" className="w-56 bg-transparent outline-none placeholder:text-slate-500" />
            </label>
            <select value={sortBy} onChange={(event) => setSortBy(event.target.value as typeof sortBy)} className="rounded-md border border-slate-800 bg-slate-950/40 px-3 py-2 text-sm text-slate-300">
              <option value="market_cap">Market cap</option>
              <option value="revenue">Revenue</option>
              <option value="return_1y">1Y return</option>
              <option value="name">Name</option>
            </select>
          </div>
        </div>
        {companies.isLoading ? <div className="p-6 text-sm text-slate-400">Loading companies...</div> : null}
        {!companies.isLoading && !companies.data?.length ? <div className="p-6 text-sm text-slate-400">No companies loaded yet.</div> : null}
        <div className="divide-y divide-slate-800">
          {filteredCompanies.map((company) => (
            <button key={company.id} onClick={() => onSelectCompany(company.id)} className="grid w-full grid-cols-1 gap-3 px-4 py-4 text-left hover:bg-slate-800/60 md:grid-cols-[2fr_1fr_1fr_1fr_1fr_1fr]">
              <div className="flex items-center gap-3">
                <Building2 className="text-sky-300" size={20} />
                <div>
                  <div className="font-semibold text-slate-100">{company.name}</div>
                  <div className="text-sm text-slate-400">{company.industry}</div>
                </div>
              </div>
              {isArchiveData ? (
                <>
                  <Cell label="Price" value={rupee(company.current_price)} />
                  <Cell label="Market Cap" value={crore(company.market_cap)} />
                  <Cell label="PE / PB" value={`${company.pe_ratio?.toFixed(1) ?? "N/A"} / ${company.price_to_book?.toFixed(1) ?? "N/A"}`} />
                  <Cell label="ROE / ROCE" value={`${percent(company.return_on_equity)} / ${percent(company.roce)}`} />
                  <Cell label="1Y Return" value={percent(company.return_1y)} />
                </>
              ) : (
                <>
                  <Cell label="Period" value={company.latest_period ?? "N/A"} />
                  <Cell label="Revenue" value={money(company.latest_revenue)} />
                  <Cell label="EBITDA" value={money(company.latest_ebitda)} />
                  <Cell label="Revenue Growth" value={percent(company.revenue_growth)} />
                </>
              )}
            </button>
          ))}
        </div>
      </section>

      {hasCompanies ? (
        <>
          <ExceptionCenter onOpenCompany={onSelectCompany} />
          <ComparisonPage />
        </>
      ) : null}
    </main>
  );
}

function Cell({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <div className="text-xs uppercase tracking-wide text-slate-500">{label}</div>
      <div className="mt-1 text-sm font-medium text-slate-100">{value}</div>
    </div>
  );
}
