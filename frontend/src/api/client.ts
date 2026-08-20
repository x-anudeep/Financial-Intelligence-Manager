import type { CompanyDetail, CompanySummary } from "../types/financial";

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000/api";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, options);
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.detail ?? `Request failed: ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export const api = {
  seed: () => request<{ rows: number; companies: string[] }>("/seed", { method: "POST" }),
  companies: () => request<CompanySummary[]>("/companies"),
  company: (id: number) => request<CompanyDetail>(`/companies/${id}`),
  uploadFinancials: async (file: File) => {
    const formData = new FormData();
    formData.append("file", file);
    return request<{ rows: number; companies: string[]; metrics: string[] }>("/financials/upload", {
      method: "POST",
      body: formData
    });
  }
};
