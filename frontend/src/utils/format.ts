export function money(value?: number | null): string {
  if (value == null) return "N/A";
  return new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", notation: "compact", maximumFractionDigits: 1 }).format(value);
}

export function rupee(value?: number | null): string {
  if (value == null) return "N/A";
  return new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 2 }).format(value);
}

export function crore(value?: number | null): string {
  if (value == null) return "N/A";
  return `${new Intl.NumberFormat("en-IN", { maximumFractionDigits: 1 }).format(value)} Cr`;
}

export function percent(value?: number | null): string {
  if (value == null) return "N/A";
  return `${(value * 100).toFixed(1)}%`;
}

export function number(value?: number | null): string {
  if (value == null) return "N/A";
  return value.toFixed(2);
}

export function compact(value?: number | null): string {
  if (value == null) return "N/A";
  return new Intl.NumberFormat("en-IN", { notation: "compact", maximumFractionDigits: 1 }).format(value);
}
