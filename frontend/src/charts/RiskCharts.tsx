import { Bar, BarChart, CartesianGrid, Cell, Legend, ResponsiveContainer, Scatter, ScatterChart, Tooltip, XAxis, YAxis } from "recharts";
import type { ComparisonRow, PortfolioRisk } from "../types/financial";

const COLORS = ["#dc2626", "#ea580c", "#d97706", "#475569", "#2563eb", "#0f766e"];

export function SeverityDistribution({ risk }: { risk?: PortfolioRisk }) {
  const data = Object.entries(risk?.severity_distribution ?? {}).map(([name, value]) => ({ name, value }));
  return (
    <ChartFrame title="Anomaly Severity Distribution">
      <ResponsiveContainer width="100%" height={220}>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="name" />
          <YAxis allowDecimals={false} />
          <Tooltip />
          <Bar dataKey="value">
            {data.map((_, index) => <Cell key={index} fill={COLORS[index % COLORS.length]} />)}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </ChartFrame>
  );
}

export function CategoryDistribution({ risk }: { risk?: PortfolioRisk }) {
  const data = Object.entries(risk?.anomaly_categories ?? {}).map(([name, value]) => ({ name, value }));
  return (
    <ChartFrame title="Most Common Anomaly Categories">
      <ResponsiveContainer width="100%" height={220}>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="name" hide />
          <YAxis allowDecimals={false} />
          <Tooltip />
          <Legend />
          <Bar dataKey="value" fill="#2563eb" />
        </BarChart>
      </ResponsiveContainer>
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
    <section className="rounded-md border border-line bg-white p-4 shadow-sm">
      <h3 className="mb-4 text-sm font-semibold uppercase tracking-wide text-slate-600">{title}</h3>
      {children}
    </section>
  );
}
