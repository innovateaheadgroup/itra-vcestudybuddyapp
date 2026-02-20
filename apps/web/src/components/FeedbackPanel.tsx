import type { FeedbackObject } from '@vce-prep-buddy/shared'

export function FeedbackPanel({
  feedback,
  whereMarksWereLost,
  commonMistakes,
  upgradeResponse,
}: {
  feedback: FeedbackObject
  whereMarksWereLost: string[]
  commonMistakes: string[]
  upgradeResponse: Record<string, unknown>
}) {
  return (
    <section className="space-y-4 rounded-xl border bg-white p-4 shadow-sm">
      <div className="flex items-end justify-between">
        <h3 className="text-lg font-semibold">Teacher-like feedback</h3>
        <p className="text-sm font-bold text-brand-700">
          {feedback.score}/{feedback.max_score}
        </p>
      </div>

      <div>
        <h4 className="mb-2 text-sm font-semibold">Rubric breakdown</h4>
        <div className="space-y-2">
          {feedback.criteria.map((criterion) => (
            <div key={criterion.name} className="rounded border bg-slate-50 p-2 text-sm">
              <p className="font-medium">
                {criterion.name}: {criterion.score}/{criterion.max}
              </p>
              <ul className="ml-4 list-disc text-xs text-slate-600">
                {criterion.notes.map((note) => (
                  <li key={note}>{note}</li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </div>

      <div>
        <h4 className="text-sm font-semibold">Where marks were lost</h4>
        <ul className="ml-4 list-disc text-sm text-slate-700">
          {whereMarksWereLost.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      </div>

      <div>
        <h4 className="text-sm font-semibold">Common mistakes</h4>
        <div className="mt-1 flex flex-wrap gap-2">
          {commonMistakes.map((tag) => (
            <span key={tag} className="rounded bg-rose-100 px-2 py-0.5 text-xs text-rose-700">
              {tag}
            </span>
          ))}
        </div>
      </div>

      <div>
        <h4 className="text-sm font-semibold">Recommended drills</h4>
        <ul className="ml-4 list-disc text-sm text-slate-700">
          {feedback.drills.map((drill) => (
            <li key={`${drill.topic_id}-${drill.count}`}>
              Topic {drill.topic_id}: {drill.count} questions
            </li>
          ))}
        </ul>
        <a href="/quick-wins" className="mt-2 inline-block rounded bg-slate-900 px-3 py-1 text-xs font-semibold text-white">
          Add to Quick Wins
        </a>
      </div>

      <div className="rounded border border-blue-200 bg-blue-50 p-3">
        <h4 className="text-sm font-semibold text-blue-800">Upgrade my answer</h4>
        <pre className="mt-1 overflow-x-auto whitespace-pre-wrap text-xs text-blue-900">
          {JSON.stringify(upgradeResponse, null, 2)}
        </pre>
      </div>
    </section>
  )
}
