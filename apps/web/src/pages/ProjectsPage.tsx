import { useEffect, useState } from 'react'

import ReactMarkdown from 'react-markdown'
import rehypeSanitize from 'rehype-sanitize'

import { useAppContext } from '../context/AppContext'
import { api } from '../lib/api'

interface Project {
  id: number
  subject_id: number
  unit: number
  title: string
  brief_md: string
  rubric_json: Record<string, unknown>
}

interface Submission {
  id: number
  project_id: number
  submission_type: string
  content_ref: string
  reflection_md?: string
  feedback_json: Record<string, unknown>
  created_at: string
}

export function ProjectsPage() {
  const { subjectCode, unit } = useAppContext()
  const [projects, setProjects] = useState<Project[]>([])
  const [selectedProject, setSelectedProject] = useState<Project | null>(null)
  const [submissions, setSubmissions] = useState<Submission[]>([])
  const [submissionType, setSubmissionType] = useState<'code' | 'report' | 'data'>('code')
  const [contentRef, setContentRef] = useState('')
  const [reflection, setReflection] = useState('')

  async function loadProjects() {
    const subjectId = subjectCode === 'SOFTDEV' ? 1 : 2
    const data = await api.get<Project[]>(`/api/projects?subject_id=${subjectId}&unit=${Math.min(unit, 2)}`)
    setProjects(data)
    if (!selectedProject && data.length > 0) {
      setSelectedProject(data[0])
    }
  }

  async function loadSubmissions(projectId: number) {
    const data = await api.get<Submission[]>(`/api/projects/${projectId}/submissions`)
    setSubmissions(data)
  }

  useEffect(() => {
    void loadProjects()
  }, [subjectCode, unit])

  useEffect(() => {
    if (!selectedProject) return
    void loadSubmissions(selectedProject.id)
  }, [selectedProject])

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-bold">Projects (Units 1-2)</h2>
      {unit > 2 ? (
        <p className="rounded border border-amber-200 bg-amber-50 p-3 text-sm">
          Projects module is primarily for Foundation Track Units 1-2.
        </p>
      ) : null}

      <div className="grid gap-4 lg:grid-cols-[260px_1fr]">
        <section className="rounded-xl border bg-white p-4 shadow-sm">
          <h3 className="text-base font-semibold">Project list</h3>
          <ul className="mt-2 space-y-2">
            {projects.map((project) => (
              <li key={project.id}>
                <button
                  className={`w-full rounded border px-3 py-2 text-left text-sm ${
                    selectedProject?.id === project.id ? 'border-brand-500 bg-brand-50' : 'bg-slate-50'
                  }`}
                  onClick={() => setSelectedProject(project)}
                >
                  Unit {project.unit}: {project.title}
                </button>
              </li>
            ))}
          </ul>
        </section>

        {selectedProject && (
          <section className="space-y-4 rounded-xl border bg-white p-4 shadow-sm">
            <h3 className="text-lg font-semibold">{selectedProject.title}</h3>
            <div className="prose prose-sm max-w-none">
              <ReactMarkdown rehypePlugins={[rehypeSanitize]}>{selectedProject.brief_md}</ReactMarkdown>
            </div>
            <div>
              <h4 className="font-semibold">Rubric</h4>
              <pre className="mt-1 rounded border bg-slate-50 p-2 text-xs">
                {JSON.stringify(selectedProject.rubric_json, null, 2)}
              </pre>
            </div>

            <div className="rounded border bg-slate-50 p-3">
              <h4 className="font-semibold">Submit work</h4>
              <div className="mt-2 grid gap-2 md:grid-cols-3">
                <select
                  value={submissionType}
                  onChange={(e) => setSubmissionType(e.target.value as 'code' | 'report' | 'data')}
                  className="rounded border px-2 py-1 text-sm"
                >
                  {['code', 'report', 'data'].map((type) => (
                    <option key={type} value={type}>
                      {type}
                    </option>
                  ))}
                </select>
                <input
                  value={contentRef}
                  onChange={(e) => setContentRef(e.target.value)}
                  placeholder="URL or text reference"
                  className="rounded border px-2 py-1 text-sm"
                />
                <input
                  value={reflection}
                  onChange={(e) => setReflection(e.target.value)}
                  placeholder="Reflection"
                  className="rounded border px-2 py-1 text-sm"
                />
              </div>
              <button
                className="mt-2 rounded bg-brand-500 px-4 py-2 text-sm font-semibold text-white"
                onClick={async () => {
                  await api.post('/api/projects/submissions', {
                    project_id: selectedProject.id,
                    submission_type: submissionType,
                    content_ref: contentRef,
                    reflection_md: reflection,
                  })
                  await loadSubmissions(selectedProject.id)
                  setContentRef('')
                  setReflection('')
                }}
              >
                Submit
              </button>
            </div>

            <div>
              <h4 className="font-semibold">Your submissions</h4>
              <div className="mt-2 space-y-2">
                {submissions.map((submission) => (
                  <article key={submission.id} className="rounded border bg-slate-50 p-3 text-sm">
                    <p>
                      {submission.submission_type} • {new Date(submission.created_at).toLocaleString()}
                    </p>
                    <p className="text-slate-600">{submission.content_ref}</p>
                    <pre className="mt-1 text-xs">{JSON.stringify(submission.feedback_json, null, 2)}</pre>
                  </article>
                ))}
              </div>
            </div>
          </section>
        )}
      </div>
    </div>
  )
}
