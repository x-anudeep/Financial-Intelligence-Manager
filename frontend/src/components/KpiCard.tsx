type Props = {
  label: string;
  value: string;
  sublabel?: string;
};

export function KpiCard({ label, value, sublabel }: Props) {
  return (
    <div className="metric-card">
      <div className="text-xs font-semibold uppercase tracking-wide text-slate-500">{label}</div>
      <div className="mt-2 text-2xl font-semibold text-ink">{value}</div>
      {sublabel ? <div className="mt-1 text-sm text-slate-500">{sublabel}</div> : null}
    </div>
  );
}
