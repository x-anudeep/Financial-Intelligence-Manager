import type { AnalystAnswer, Anomaly, CompanyDetail, CompanySummary, ComparisonRow, DocumentRecord, PortfolioRisk } from "../types/financial";

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
  anomalies: (params = "") => request<Anomaly[]>(`/anomalies${params}`),
  portfolioRisk: () => request<PortfolioRisk>("/portfolio/risk"),
  compare: (ids: number[]) => request<{ companies: ComparisonRow[] }>(`/comparison?${ids.map((id) => `company_ids=${id}`).join("&")}`),
  documents: (companyId: number) => request<DocumentRecord[]>(`/companies/${companyId}/documents`),
  uploadDocument: async (companyId: number, file: File) => {
    const formData = new FormData();
    formData.append("file", file);
    return request<{ document_id: number; chunks: number; processing_status: string }>(`/companies/${companyId}/documents`, { method: "POST", body: formData });
  },
  analystSummary: (companyId: number) => request<AnalystAnswer>(`/companies/${companyId}/analyst-summary`),
  askAnalyst: (companyId: number, question: string) => request<AnalystAnswer>("/assistant/ask", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ company_id: companyId, question })
  }),
  supportingContext: (anomalyId: number) => request<AnalystAnswer>("/anomalies/supporting-context", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ anomaly_id: anomalyId })
  }),
  uploadFinancials: async (file: File) => {
    const formData = new FormData();
    formData.append("file", file);
    return request<{ rows: number; companies: string[]; metrics: string[] }>("/financials/upload", {
      method: "POST",
      body: formData
    });
  }
};
