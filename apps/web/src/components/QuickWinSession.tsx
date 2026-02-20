interface QuickWinItem {
  id: number
  topic_id: number | null
  question_id: number | null
  next_due_at: string
  interval_days: number
  ease_factor: number
}

export function QuickWinSession({
  items,
  streak,
  masteryTrend,
  onReview,
}: {
  items: QuickWinItem[]
  streak: number
  masteryTrend: number[]
  onReview: (id: number, correct: boolean) => void
}) {
  return (
    <section className="space-y-4 rounded-xl border bg-white p-4 shadow-sm">
      <div className="flex items-center justify-between">
        <h3 className="text-base font-semibold">Quick Wins Session</h3>
        <span className="rounded bg-emerald-100 px-2 py-1 text-xs font-semibold text-emerald-700">
          Streak: {streak}
        </span>
      </div>

      <div>
        <p className="text-sm font-medium">Mastery trend</p>
        <div className="mt-1 flex gap-1">
          {masteryTrend.map((value, idx) => (
            <div key={`${value}-${idx}`} className="h-8 w-3 rounded bg-brand-100">
              <div className="w-full rounded bg-brand-500" style={{ height: `${Math.round(value * 100)}%` }} />
            </div>
          ))}
        </div>
      </div>

      <div className="space-y-2">
        {items.map((item) => (
          <article key={item.id} className="rounded border bg-slate-50 p-3 text-sm">
            <p>
              {item.question_id ? `Question ${item.question_id}` : `Topic ${item.topic_id}`} • Due{' '}
              {new Date(item.next_due_at).toLocaleString()}
            </p>
            <p className="text-xs text-slate-500">
              Interval: {item.interval_days}d • Ease: {item.ease_factor.toFixed(2)}
            </p>
            <div className="mt-2 flex gap-2">
              <button
                onClick={() => onReview(item.id, true)}
                className="rounded bg-emerald-500 px-2 py-1 text-xs text-white"
              >
                Correct
              </button>
              <button onClick={() => onReview(item.id, false)} className="rounded bg-rose-500 px-2 py-1 text-xs text-white">
                Incorrect
              </button>
            </div>
          </article>
        ))}
      </div>
    </section>
  )
}
