import { useState } from 'react'

import { FeedbackPanel } from '../components/FeedbackPanel'
import { useAppContext } from '../context/AppContext'
import { api } from '../lib/api'

interface BuddyResponse {
  quick_diagnosis: string
  what_to_fix_first: string[]
  hints: string[]
  mini_drill: string
  checklist_aligned_to_marks: string[]
  feedback: {
    score: number
    max_score: number
    criteria: Array<{ name: string; score: number; max: number; notes: string[] }>
    missing: string[]
    next_steps: string[]
    drills: Array<{ topic_id: number; count: number }>
    mistake_tags: string[]
    integrity_mode: 'foundation' | 'scored'
  }
}

export function BuddyPage() {
  const { unit, track } = useAppContext()
  const [prompt, setPrompt] = useState('')
  const [response, setResponse] = useState<BuddyResponse | null>(null)
  const [loading, setLoading] = useState(false)

  async function submit() {
    setLoading(true)
    try {
      const result = await api.post<BuddyResponse>('/api/buddy/chat', {
        prompt,
        unit,
        track,
        integrity_mode: track,
        marks: 4,
      })
      setResponse(result)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-bold">Buddy (AI Tutor)</h2>
      <section className="rounded-xl border bg-white p-4 shadow-sm">
        <textarea
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          className="h-32 w-full rounded border p-2 text-sm"
          placeholder="Ask Buddy for coaching (e.g. Explain why my answer only scored 2/4)..."
        />
        <button
          onClick={submit}
          disabled={loading || !prompt.trim()}
          className="mt-3 rounded bg-brand-500 px-4 py-2 text-sm font-semibold text-white disabled:opacity-50"
        >
          {loading ? 'Thinking...' : 'Get coaching feedback'}
        </button>
      </section>

      {response && (
        <section className="space-y-3 rounded-xl border bg-white p-4 shadow-sm">
          <h3 className="text-base font-semibold">Coaching response</h3>
          <div className="rounded border bg-slate-50 p-3">
            <h4 className="font-semibold">1) Quick diagnosis</h4>
            <p className="text-sm">{response.quick_diagnosis}</p>
          </div>
          <div className="rounded border bg-slate-50 p-3">
            <h4 className="font-semibold">2) What to fix first</h4>
            <ul className="ml-4 list-disc text-sm">
              {response.what_to_fix_first.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          </div>
          <div className="rounded border bg-slate-50 p-3">
            <h4 className="font-semibold">3) Hints / guiding questions</h4>
            <ul className="ml-4 list-disc text-sm">
              {response.hints.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          </div>
          <div className="rounded border bg-slate-50 p-3">
            <h4 className="font-semibold">4) Mini drill</h4>
            <p className="text-sm">{response.mini_drill}</p>
          </div>
          <div className="rounded border bg-slate-50 p-3">
            <h4 className="font-semibold">5) Checklist aligned to marks</h4>
            <ul className="ml-4 list-disc text-sm">
              {response.checklist_aligned_to_marks.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          </div>
        </section>
      )}

      {response && (
        <FeedbackPanel
          feedback={response.feedback}
          whereMarksWereLost={response.feedback.missing}
          commonMistakes={response.feedback.mistake_tags}
          upgradeResponse={{ note: 'Use this checklist to refine your draft response.' }}
        />
      )}
    </div>
  )
}
