import { Send } from "lucide-react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { api } from "../api/client";
import { SourceList } from "./SourceList";

export function AnalystCopilot({ companyId }: { companyId: number }) {
  const [question, setQuestion] = useState("Why was receivables growth flagged?");
  const summary = useQuery({ queryKey: ["analyst-summary", companyId], queryFn: () => api.analystSummary(companyId) });
  const ask = useMutation({ mutationFn: () => api.askAnalyst(companyId, question) });
  const active = ask.data ?? summary.data;

  return (
    <section className="rounded-md border border-line bg-white p-4 shadow-sm">
      <div className="mb-3 flex items-center justify-between gap-3">
        <h3 className="text-sm font-semibold uppercase tracking-wide text-slate-600">LLM Analyst Copilot</h3>
        <span className="rounded border border-line px-2 py-1 text-xs text-slate-500">{active?.ai_enabled ? "AI enabled" : "AI fallback mode"}</span>
      </div>
      <div className="flex gap-2">
        <input value={question} onChange={(event) => setQuestion(event.target.value)} className="min-w-0 flex-1 rounded-md border border-line px-3 py-2 text-sm" />
        <button onClick={() => ask.mutate()} className="inline-flex items-center gap-2 rounded-md bg-ink px-3 py-2 text-sm font-medium text-white">
          <Send size={16} /> Ask
        </button>
      </div>
      <div className="mt-4 rounded-md bg-slate-50 p-3 text-sm text-slate-700">{active?.answer ?? "Loading analyst summary..."}</div>
      <div className="mt-4">
        <SourceList sources={active?.sources ?? []} />
      </div>
    </section>
  );
}
