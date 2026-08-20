import { Area, AreaChart, Bar, BarChart, CartesianGrid, Legend, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import type { MetricPoint } from "../types/financial";

function axisMoney(value: number) {
  return `$${Math.round(value / 1_000_000)}M`;
}

export function RevenueEbitdaChart({ data }: { data: MetricPoint[] }) {
  return (
    <ChartFrame title="Revenue and EBITDA">
      <ResponsiveContainer width="100%" height={260}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="period" />
          <YAxis tickFormatter={axisMoney} />
          <Tooltip formatter={(value) => axisMoney(Number(value))} />
          <Legend />
          <Line type="monotone" dataKey="revenue" stroke="#2563eb" strokeWidth={2} />
          <Line type="monotone" dataKey="ebitda" stroke="#16a34a" strokeWidth={2} />
        </LineChart>
      </ResponsiveContainer>
    </ChartFrame>
  );
}

export function CashDebtChart({ data }: { data: MetricPoint[] }) {
  return (
    <ChartFrame title="Cash vs Debt">
      <ResponsiveContainer width="100%" height={260}>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="period" />
          <YAxis tickFormatter={axisMoney} />
          <Tooltip formatter={(value) => axisMoney(Number(value))} />
          <Legend />
          <Bar dataKey="cash" fill="#0f766e" />
          <Bar dataKey="total_debt" fill="#b91c1c" />
        </BarChart>
      </ResponsiveContainer>
    </ChartFrame>
  );
}

export function BankIncomeChart({ data }: { data: MetricPoint[] }) {
  return (
    <ChartFrame title="Bank Revenue Mix">
      <ResponsiveContainer width="100%" height={260}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="period" />
          <YAxis tickFormatter={axisMoney} />
          <Tooltip formatter={(value) => axisMoney(Number(value))} />
          <Legend />
          <Line type="monotone" dataKey="net_interest_income" name="net interest income" stroke="#38bdf8" strokeWidth={2} />
          <Line type="monotone" dataKey="noninterest_income" name="noninterest income" stroke="#a78bfa" strokeWidth={2} />
          <Line type="monotone" dataKey="net_income" name="net income" stroke="#22c55e" strokeWidth={2} />
        </LineChart>
      </ResponsiveContainer>
    </ChartFrame>
  );
}

export function BankBalanceSheetChart({ data }: { data: MetricPoint[] }) {
  return (
    <ChartFrame title="Deposits and Loans">
      <ResponsiveContainer width="100%" height={260}>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="period" />
          <YAxis tickFormatter={axisMoney} />
          <Tooltip formatter={(value) => axisMoney(Number(value))} />
          <Legend />
          <Bar dataKey="deposits" fill="#0f766e" />
          <Bar dataKey="loans" fill="#2563eb" />
        </BarChart>
      </ResponsiveContainer>
    </ChartFrame>
  );
}

export function MarginChart({ data }: { data: MetricPoint[] }) {
  const marginData = data.map((row) => ({ ...row, ebitda_margin_pct: row.ebitda_margin == null ? null : row.ebitda_margin * 100 }));
  return (
    <ChartFrame title="EBITDA Margin Trend">
      <ResponsiveContainer width="100%" height={260}>
        <AreaChart data={marginData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="period" />
          <YAxis tickFormatter={(value) => `${value}%`} />
          <Tooltip formatter={(value) => `${Number(value).toFixed(1)}%`} />
          <Area type="monotone" dataKey="ebitda_margin_pct" stroke="#7c3aed" fill="#ddd6fe" />
        </AreaChart>
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
