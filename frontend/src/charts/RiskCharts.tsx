import { Bar, BarChart, CartesianGrid, Cell, Legend, ResponsiveContainer, Scatter, ScatterChart, Tooltip, XAxis, YAxis } from "recharts";
import type { ComparisonRow, PortfolioRisk } from "../types/financial";

const COLORS = ["#dc2626", "#ea580c", "#d97706", "#475569", "#2563eb", "#0f766e"];

export function SeverityDistribution({ risk }: { risk?: PortfolioRisk }) {
  const data = Object.entries(risk?.severity_distribution ?? {}).map(([name, value]) => ({ name, value }));
  return (
    <ChartFrame title="Anomaly Severity Distribution">
      {data.length ? (
        <ResponsiveContainer width="100%" height={220}>
          <BarChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
            <XAxis dataKey="name" stroke="#94a3b8" />
            <YAxis allowDecimals={false} stroke="#94a3b8" />
            <Tooltip />
            <Bar dataKey="value">
              {data.map((_, index) => <Cell key={index} fill={COLORS[index % COLORS.length]} />)}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      ) : <EmptyChart text="No exceptions detected yet." />}
    </ChartFrame>
  );
}

export function CategoryDistribution({ risk }: { risk?: PortfolioRisk }) {
  const data = Object.entries(risk?.anomaly_categories ?? {}).map(([name, value]) => ({ name, value }));
  return (
    <ChartFrame title="Most Common Anomaly Categories">
      {data.length ? (
        <ResponsiveContainer width="100%" height={220}>
          <BarChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
            <XAxis dataKey="name" hide />
            <YAxis allowDecimals={false} stroke="#94a3b8" />
            <Tooltip />
            <Legend />
            <Bar dataKey="value" fill="#38bdf8" />
          </BarChart>
        </ResponsiveContainer>
      ) : <EmptyChart text="No anomaly categories to chart." />}
    </ChartFrame>
  );
}

export function LeverageMarginScatter({ data }: { data: ComparisonRow[] }) {
  const points = data.map((row) => ({ ...row, margin: (row.ebitda_margin ?? 0) * 100 }));
  return (
    <ChartFrame title="Debt / EBITDA vs EBITDA Margin">
      <ResponsiveContainer width="100%" height={260}>
        <ScatterChart>
          <CartesianGrid />
          <XAxis type="number" dataKey="debt_to_ebitda" name="Debt / EBITDA" />
          <YAxis type="number" dataKey="margin" name="EBITDA Margin" tickFormatter={(value) => `${value}%`} />
          <Tooltip cursor={{ strokeDasharray: "3 3" }} formatter={(value, name) => [typeof value === "number" ? value.toFixed(2) : value, name]} />
          <Scatter data={points} fill="#0f766e" name="Companies" />
        </ScatterChart>
      </ResponsiveContainer>
    </ChartFrame>
  );
}

function ChartFrame({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="rounded-md border border-slate-800 bg-slate-900/80 p-4 shadow-sm shadow-black/20">
      <h3 className="mb-4 text-sm font-semibold uppercase tracking-wide text-slate-300">{title}</h3>
      {children}
    </section>
  );
}

function EmptyChart({ text }: { text: string }) {
  return <div className="flex h-[220px] items-center justify-center rounded-md border border-dashed border-slate-700 bg-slate-950/30 text-sm text-slate-500">{text}</div>;
}
