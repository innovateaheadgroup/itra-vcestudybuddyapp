import type { TopicCard as TopicCardData } from '../lib/api'

export function TopicCard({ data, onPractice }: { data: TopicCardData; onPractice?: () => void }) {
  const statusColor = {
    'Not started': 'bg-slate-100 text-slate-700',
    Learning: 'bg-blue-100 text-blue-700',
    Practising: 'bg-amber-100 text-amber-700',
    Ready: 'bg-emerald-100 text-emerald-700',
  }[data.status]

  return (
    <article className="rounded-xl border bg-white p-4 shadow-sm">
      <div className="mb-2 flex items-center justify-between">
        <h3 className="text-sm font-semibold text-slate-900">{data.topic.title}</h3>
        <span className={`rounded px-2 py-1 text-xs ${statusColor}`}>{data.status}</span>
      </div>
      <p className="text-xs text-slate-500">
        Unit {data.topic.unit} • {data.topic.aos} • {data.topic.outcome}
      </p>
      <div className="mt-3">
        <div className="mb-1 flex justify-between text-xs text-slate-500">
          <span>Mastery</span>
          <span>{data.mastery_pct}%</span>
        </div>
        <div className="h-2 rounded-full bg-slate-100">
          <div className="h-2 rounded-full bg-brand-500" style={{ width: `${data.mastery_pct}%` }} />
        </div>
      </div>
      <div className="mt-3 flex items-center justify-between">
        <span className="text-xs text-slate-500">~{data.estimated_time} mins</span>
        {onPractice && (
          <button
            onClick={onPractice}
            className="rounded bg-brand-500 px-3 py-1 text-xs font-semibold text-white hover:bg-brand-700"
          >
            Practice
          </button>
        )}
      </div>
    </article>
  )
}
