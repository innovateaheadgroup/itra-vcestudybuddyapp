import { useEffect, useState } from 'react'

import { EvidenceTimeline } from '../components/EvidenceTimeline'
import { useAppContext } from '../context/AppContext'
import { api } from '../lib/api'

interface SatProject {
  id: number
  subject_id: number
  title: string
  context_md: string
}

interface Milestone {
  id: number
  part: number
  checklist_json: Record<string, unknown>
  status_json: Record<string, unknown>
  due_dates_json: Record<string, unknown>
}

interface Evidence {
  id: number
  entry_type: string
  content_md: string
  created_at: string
}

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

export function SatHubPage() {
  const { subjectCode, unit } = useAppContext()
  const [projects, setProjects] = useState<SatProject[]>([])
  const [selectedProjectId, setSelectedProjectId] = useState<number | null>(null)
  const [milestones, setMilestones] = useState<Milestone[]>([])
  const [evidence, setEvidence] = useState<Evidence[]>([])
  const [title, setTitle] = useState('')
  const [contextMd, setContextMd] = useState('')
  const [logType, setLogType] = useState<'decision' | 'test' | 'feedback' | 'reflection'>('decision')
  const [logContent, setLogContent] = useState('')

  async function loadProjects() {
    const data = await api.get<SatProject[]>('/api/sat/projects')
    setProjects(data)
  }

  async function loadProjectDetails(projectId: number) {
    const [milestoneData, evidenceData] = await Promise.all([
      api.get<Milestone[]>(`/api/sat/projects/${projectId}/milestones`),
      api.get<Evidence[]>(`/api/sat/projects/${projectId}/evidence`),
    ])
    setMilestones(milestoneData)
    setEvidence(evidenceData)
  }

  useEffect(() => {
    void loadProjects()
  }, [])

  useEffect(() => {
    if (!selectedProjectId) return
    void loadProjectDetails(selectedProjectId)
  }, [selectedProjectId])

  if (unit <= 2) {
    return (
      <div className="rounded-xl border border-amber-300 bg-amber-50 p-4">
        SAT Hub is only available for Units 3-4 (Scored Track).
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-bold">SAT Hub</h2>
      <section className="rounded-xl border bg-white p-4 shadow-sm">
        <h3 className="text-base font-semibold">Create SAT project tracker</h3>
        <div className="mt-2 grid gap-2 md:grid-cols-2">
          <input
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Project title"
            className="rounded border px-2 py-1 text-sm"
          />
          <textarea
            value={contextMd}
            onChange={(e) => setContextMd(e.target.value)}
            placeholder="Context"
            className="rounded border px-2 py-1 text-sm"
          />
        </div>
        <button
          className="mt-2 rounded bg-brand-500 px-4 py-2 text-sm font-semibold text-white"
          onClick={async () => {
            const created = await api.post<SatProject>('/api/sat/projects', {
              subject_id: subjectCode === 'SOFTDEV' ? 1 : 2,
              title,
              context_md: contextMd,
            })
            await loadProjects()
            setSelectedProjectId(created.id)
          }}
        >
          Create
        </button>
      </section>

      <section className="rounded-xl border bg-white p-4 shadow-sm">
        <h3 className="text-base font-semibold">Projects</h3>
        <ul className="mt-2 space-y-2">
          {projects.map((project) => (
            <li key={project.id}>
              <button
                className={`w-full rounded border px-3 py-2 text-left text-sm ${
                  selectedProjectId === project.id ? 'border-brand-500 bg-brand-50' : 'bg-slate-50'
                }`}
                onClick={() => setSelectedProjectId(project.id)}
              >
                {project.title}
              </button>
            </li>
          ))}
        </ul>
      </section>

      {selectedProjectId && (
        <>
          <section className="rounded-xl border bg-white p-4 shadow-sm">
            <div className="flex items-center justify-between">
              <h3 className="text-base font-semibold">Milestones</h3>
              <a
                href={`${API_BASE_URL}/api/sat/${selectedProjectId}/export`}
                target="_blank"
                className="rounded bg-slate-900 px-3 py-1 text-xs font-semibold text-white"
                rel="noreferrer"
              >
                Export HTML pack
              </a>
            </div>
            <div className="mt-2 grid gap-2 md:grid-cols-2">
              {milestones.map((milestone) => (
                <article key={milestone.id} className="rounded border bg-slate-50 p-3">
                  <h4 className="font-semibold">Part {milestone.part}</h4>
                  <pre className="mt-1 text-xs">{JSON.stringify(milestone.checklist_json, null, 2)}</pre>
                </article>
              ))}
            </div>
          </section>

          <section className="rounded-xl border bg-white p-4 shadow-sm">
            <h3 className="text-base font-semibold">Evidence log</h3>
            <div className="mt-2 flex flex-wrap gap-2">
              <select value={logType} onChange={(e) => setLogType(e.target.value as typeof logType)} className="rounded border px-2 py-1 text-sm">
                {['decision', 'test', 'feedback', 'reflection'].map((type) => (
                  <option key={type} value={type}>
                    {type}
                  </option>
                ))}
              </select>
              <input
                value={logContent}
                onChange={(e) => setLogContent(e.target.value)}
                className="min-w-80 rounded border px-2 py-1 text-sm"
                placeholder="Evidence note"
              />
              <button
                className="rounded bg-brand-500 px-3 py-1 text-sm font-semibold text-white"
                onClick={async () => {
                  await api.post('/api/sat/evidence', {
                    sat_project_id: selectedProjectId,
                    entry_type: logType,
                    content_md: logContent,
                    attachment_refs_json: { urls: [] },
                  })
                  await loadProjectDetails(selectedProjectId)
                  setLogContent('')
                }}
              >
                Add
              </button>
            </div>
          </section>

          <EvidenceTimeline items={evidence} />
        </>
      )}
    </div>
  )
}
