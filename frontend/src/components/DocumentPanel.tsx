import { FileText, Upload } from "lucide-react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "../api/client";

export function DocumentPanel({ companyId }: { companyId: number }) {
  const queryClient = useQueryClient();
  const documents = useQuery({ queryKey: ["documents", companyId], queryFn: () => api.documents(companyId) });
  const upload = useMutation({ mutationFn: (file: File) => api.uploadDocument(companyId, file), onSuccess: () => queryClient.invalidateQueries({ queryKey: ["documents", companyId] }) });
  return (
    <section className="rounded-md border border-line bg-white p-4 shadow-sm">
      <div className="mb-3 flex items-center justify-between gap-3">
        <h3 className="text-sm font-semibold uppercase tracking-wide text-slate-600">Supporting Documents</h3>
        <label className="inline-flex cursor-pointer items-center gap-2 rounded-md border border-line px-3 py-2 text-sm font-medium">
          <Upload size={16} /> Upload PDF/TXT
          <input className="hidden" type="file" accept=".pdf,.txt,.md" onChange={(event) => event.target.files?.[0] && upload.mutate(event.target.files[0])} />
        </label>
      </div>
      {upload.error ? <div className="mb-3 rounded-md border border-red-200 bg-red-50 p-2 text-sm text-red-700">{upload.error.message}</div> : null}
      <div className="space-y-2">
        {documents.data?.map((doc) => (
          <div key={doc.id} className="flex items-center justify-between rounded-md border border-line p-2 text-sm">
            <span className="inline-flex items-center gap-2"><FileText size={16} /> {doc.file_name}</span>
            <span className="text-slate-500">{doc.processing_status}</span>
          </div>
        ))}
        {!documents.data?.length ? <div className="text-sm text-slate-500">No supporting documents uploaded yet.</div> : null}
      </div>
    </section>
  );
}
