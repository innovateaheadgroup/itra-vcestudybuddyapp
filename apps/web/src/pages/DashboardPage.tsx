import { useQuery } from '@tanstack/react-query'

import { api } from '../lib/api'

export function DashboardPage() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['dashboard'],
    queryFn: () => api.get<{
      attempts_last_7_days: number
      average_score_ratio: number
      quickwins_due: number
      weak_topics: number
    }>('/api/dashboard'),
  })

  if (isLoading) return <p>Loading dashboard...</p>
  if (error) return <p className="text-rose-600">Failed to load dashboard.</p>

  const cards = [
    { label: 'Attempts (7 days)', value: data?.attempts_last_7_days ?? 0 },
    { label: 'Average score ratio', value: `${Math.round((data?.average_score_ratio ?? 0) * 100)}%` },
    { label: 'Quick Wins due', value: data?.quickwins_due ?? 0 },
    { label: 'Weak topics', value: data?.weak_topics ?? 0 },
  ]

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-bold">Dashboard</h2>
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        {cards.map((card) => (
          <article key={card.label} className="rounded-xl border bg-white p-4 shadow-sm">
            <p className="text-xs text-slate-500">{card.label}</p>
            <p className="mt-2 text-2xl font-bold text-slate-900">{card.value}</p>
          </article>
        ))}
      </div>
    </div>
  )
}
