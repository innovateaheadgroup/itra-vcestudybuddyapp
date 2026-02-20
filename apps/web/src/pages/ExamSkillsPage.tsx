import { useMemo, useState } from 'react'

import { useQuery } from '@tanstack/react-query'

import { useAppContext } from '../context/AppContext'
import { api } from '../lib/api'

interface CommandTerm {
  term: string
  definition: string
  checklist: string[]
  example: string
}

interface ExamTemplate {
  id: string
  title: string
  structure: string[]
  example: string
}

export function ExamSkillsPage() {
  const { unit, track } = useAppContext()
  const [minutes, setMinutes] = useState(20)
  const [caseText, setCaseText] = useState('')
  const [tags, setTags] = useState({
    constraints: '',
    stakeholders: '',
    requirements: '',
    data_types: '',
    risks_ethics: '',
  })
  const [answerPlan, setAnswerPlan] = useState<Record<string, unknown> | null>(null)
  const [timedSet, setTimedSet] = useState<Record<string, unknown> | null>(null)

  const commandTerms = useQuery({
    queryKey: ['exam-skills-command-terms'],
    queryFn: () => api.get<CommandTerm[]>('/api/exam-skills/command-terms'),
  })
  const templates = useQuery({
    queryKey: ['exam-skills-templates'],
    queryFn: () => api.get<ExamTemplate[]>('/api/exam-skills/templates'),
  })

  const tagsPayload = useMemo(
    () => ({
      constraints: tags.constraints.split(',').map((value) => value.trim()),
      stakeholders: tags.stakeholders.split(',').map((value) => value.trim()),
      requirements: tags.requirements.split(',').map((value) => value.trim()),
      data_types: tags.data_types.split(',').map((value) => value.trim()),
      risks_ethics: tags.risks_ethics.split(',').map((value) => value.trim()),
    }),
    [tags],
  )

  async function generateTimedSet() {
    const response = await api.get<Record<string, unknown>>(
      `/api/exam-skills/timed-practice?unit=${unit}&minutes=${minutes}`,
    )
    setTimedSet(response)
  }

  async function generateAnswerPlan() {
    const response = await api.post<Record<string, unknown>>('/api/exam-skills/case-study/answer-plan', {
      case_text: caseText,
      tags: tagsPayload,
      integrity_mode: track,
    })
    setAnswerPlan(response)
  }

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-bold">Exam Skills</h2>

      <section className="rounded-xl border bg-white p-4 shadow-sm">
        <h3 className="text-base font-semibold">Command Terms</h3>
        <div className="mt-3 grid gap-3 md:grid-cols-2">
          {(commandTerms.data ?? []).map((item) => (
            <article key={item.term} className="rounded border bg-slate-50 p-3">
              <h4 className="font-semibold capitalize">{item.term}</h4>
              <p className="text-sm text-slate-600">{item.definition}</p>
              <ul className="ml-4 list-disc text-xs text-slate-700">
                {item.checklist.map((point) => (
                  <li key={point}>{point}</li>
                ))}
              </ul>
              <p className="mt-1 text-xs text-slate-500">Example: {item.example}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="rounded-xl border bg-white p-4 shadow-sm">
        <h3 className="text-base font-semibold">Templates</h3>
        <div className="mt-3 space-y-2">
          {(templates.data ?? []).map((template) => (
            <article key={template.id} className="rounded border bg-slate-50 p-3">
              <h4 className="font-semibold">{template.title}</h4>
              <ul className="ml-4 list-disc text-xs text-slate-700">
                {template.structure.map((part) => (
                  <li key={part}>{part}</li>
                ))}
              </ul>
              <p className="mt-1 text-xs text-slate-500">{template.example}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="rounded-xl border bg-white p-4 shadow-sm">
        <h3 className="text-base font-semibold">Timed practice</h3>
        <div className="mt-2 flex items-end gap-3">
          <label className="text-sm">
            Minutes
            <select
              value={minutes}
              onChange={(e) => setMinutes(Number(e.target.value))}
              className="ml-2 rounded border px-2 py-1"
            >
              {[10, 20, 30, 45].map((value) => (
                <option key={value} value={value}>
                  {value}
                </option>
              ))}
            </select>
          </label>
          <button className="rounded bg-brand-500 px-4 py-2 text-sm font-semibold text-white" onClick={generateTimedSet}>
            Generate from weak areas
          </button>
        </div>
        {timedSet ? (
          <pre className="mt-3 overflow-x-auto rounded border bg-slate-50 p-3 text-xs">{JSON.stringify(timedSet, null, 2)}</pre>
        ) : null}
      </section>

      <section className="rounded-xl border bg-white p-4 shadow-sm">
        <h3 className="text-base font-semibold">Case study annotation tool</h3>
        <textarea
          value={caseText}
          onChange={(e) => setCaseText(e.target.value)}
          placeholder="Paste case text..."
          className="mt-2 h-32 w-full rounded border p-2 text-sm"
        />
        <div className="mt-3 grid gap-2 md:grid-cols-2">
          {Object.entries(tags).map(([key, value]) => (
            <label key={key} className="text-xs uppercase tracking-wide text-slate-500">
              {key.replaceAll('_', ' ')}
              <input
                value={value}
                onChange={(e) => setTags((prev) => ({ ...prev, [key]: e.target.value }))}
                placeholder="comma-separated tags"
                className="mt-1 w-full rounded border px-2 py-1 text-sm normal-case tracking-normal"
              />
            </label>
          ))}
        </div>
        <button className="mt-3 rounded bg-brand-500 px-4 py-2 text-sm font-semibold text-white" onClick={generateAnswerPlan}>
          Generate answer plan
        </button>
        {answerPlan ? (
          <pre className="mt-3 overflow-x-auto rounded border bg-slate-50 p-3 text-xs">{JSON.stringify(answerPlan, null, 2)}</pre>
        ) : null}
      </section>
    </div>
  )
}
