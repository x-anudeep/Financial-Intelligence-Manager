const COLORS: Record<string, string> = {
  critical: "bg-red-100 text-red-800 border-red-200",
  high: "bg-orange-100 text-orange-800 border-orange-200",
  medium: "bg-amber-100 text-amber-800 border-amber-200",
  low: "bg-slate-100 text-slate-700 border-slate-200"
};

export function SeverityBadge({ severity }: { severity: string }) {
  return <span className={`inline-flex rounded border px-2 py-1 text-xs font-semibold uppercase ${COLORS[severity] ?? COLORS.low}`}>{severity}</span>;
}
