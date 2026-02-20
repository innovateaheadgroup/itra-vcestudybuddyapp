interface EvidenceItem {
  id: number
  entry_type: string
  content_md: string
  created_at: string
}

export function EvidenceTimeline({ items }: { items: EvidenceItem[] }) {
  return (
    <section className="rounded-xl border bg-white p-4 shadow-sm">
      <h3 className="mb-3 text-base font-semibold">Evidence timeline</h3>
      <div className="space-y-3">
        {items.map((item) => (
          <article key={item.id} className="border-l-4 border-brand-500 bg-slate-50 p-3">
            <div className="mb-1 flex items-center justify-between text-xs text-slate-500">
              <span className="rounded bg-slate-200 px-2 py-0.5">{item.entry_type}</span>
              <span>{new Date(item.created_at).toLocaleString()}</span>
            </div>
            <p className="text-sm text-slate-700">{item.content_md}</p>
          </article>
        ))}
      </div>
    </section>
  )
}
