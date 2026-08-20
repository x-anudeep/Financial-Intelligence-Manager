export function money(value?: number | null): string {
  if (value == null) return "N/A";
  return new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", notation: "compact", maximumFractionDigits: 1 }).format(value);
}

export function percent(value?: number | null): string {
  if (value == null) return "N/A";
  return `${(value * 100).toFixed(1)}%`;
}

export function number(value?: number | null): string {
  if (value == null) return "N/A";
  return value.toFixed(2);
}
