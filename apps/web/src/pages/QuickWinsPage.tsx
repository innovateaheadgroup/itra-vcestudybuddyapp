import { useState } from 'react'

import { useMutation } from '@tanstack/react-query'

import { QuickWinSession } from '../components/QuickWinSession'
import { api } from '../lib/api'

interface SessionPayload {
  items: Array<{
    id: number
    topic_id: number | null
    question_id: number | null
    next_due_at: string
    interval_days: number
    ease_factor: number
  }>
  streak: number
  mastery_trend: number[]
}

export function QuickWinsPage() {
  const [minutes, setMinutes] = useState<5 | 10 | 15>(10)
  const [session, setSession] = useState<SessionPayload | null>(null)

  const buildSession = useMutation({
    mutationFn: (selectedMinutes: 5 | 10 | 15) =>
      api.post<SessionPayload>('/api/quick-wins/session', { minutes: selectedMinutes }),
    onSuccess: setSession,
  })

  const reviewMutation = useMutation({
    mutationFn: (payload: { queue_item_id: number; correct: boolean }) => api.post('/api/quick-wins/review', payload),
    onSuccess: () => {
      buildSession.mutate(minutes)
    },
  })

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-bold">Quick Wins</h2>
      <section className="rounded-xl border bg-white p-4 shadow-sm">
        <h3 className="text-base font-semibold">Daily session generator</h3>
        <div className="mt-3 flex gap-2">
          {[5, 10, 15].map((value) => (
            <button
              key={value}
              className={`rounded px-3 py-1 text-sm ${minutes === value ? 'bg-brand-500 text-white' : 'bg-slate-100'}`}
              onClick={() => setMinutes(value as 5 | 10 | 15)}
            >
              {value} min
            </button>
          ))}
          <button
            className="rounded bg-slate-900 px-3 py-1 text-sm font-semibold text-white"
            onClick={() => buildSession.mutate(minutes)}
          >
            Generate
          </button>
        </div>
      </section>

      {session ? (
        <QuickWinSession
          items={session.items}
          streak={session.streak}
          masteryTrend={session.mastery_trend}
          onReview={(id, correct) => reviewMutation.mutate({ queue_item_id: id, correct })}
        />
      ) : null}
    </div>
  )
}
