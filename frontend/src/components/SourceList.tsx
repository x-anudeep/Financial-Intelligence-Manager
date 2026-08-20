import type { RetrievedContext } from "../types/financial";

export function SourceList({ sources }: { sources: RetrievedContext[] }) {
  if (!sources.length) return <div className="text-sm text-slate-400">No document passages were retrieved.</div>;
  return (
    <div className="space-y-3">
      {sources.map((source) => (
        <div key={source.chunk_id} className="rounded-md border border-slate-800 bg-slate-950/40 p-3">
          <div className="text-xs font-semibold uppercase tracking-wide text-slate-400">
            {source.document_name}{source.page ? ` | page ${source.page}` : ""} | score {source.score.toFixed(2)}
          </div>
          <div className="mt-2 text-sm text-slate-300">{source.content}</div>
        </div>
      ))}
    </div>
  );
}
