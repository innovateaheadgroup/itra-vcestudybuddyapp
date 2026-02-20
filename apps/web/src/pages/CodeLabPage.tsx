import { useEffect, useState } from 'react'

import { api } from '../lib/api'

interface Snapshot {
  id: number
  filename: string
  content: string
  created_at: string
}

export function CodeLabPage() {
  const [filename, setFilename] = useState('solution.py')
  const [code, setCode] = useState('def solve(x):\n    return x\n')
  const [testsPublic, setTestsPublic] = useState('assert solve(2) == 2')
  const [runOutput, setRunOutput] = useState('')
  const [snapshots, setSnapshots] = useState<Snapshot[]>([])

  async function loadSnapshots() {
    const data = await api.get<Snapshot[]>('/api/tools/code-lab/snapshots')
    setSnapshots(data)
  }

  useEffect(() => {
    void loadSnapshots()
  }, [])

  async function runCode() {
    const result = await api.post<{ passed: boolean; output: string; failed_test?: string }>(
      '/api/tools/code-lab/run',
      {
        code,
        tests_public: testsPublic,
        language: 'python',
      },
    )
    setRunOutput(`${result.passed ? 'PASS' : 'FAIL'}\n${result.output}`)
  }

  async function saveSnapshot() {
    await api.post('/api/tools/code-lab/snapshots', {
      filename,
      content: code,
      metadata_json: { tests_public: testsPublic },
    })
    await loadSnapshots()
  }

  return (
    <div className="grid gap-4 lg:grid-cols-[240px_1fr]">
      <section className="rounded-xl border bg-white p-4 shadow-sm">
        <h3 className="text-base font-semibold">File tree</h3>
        <ul className="mt-2 space-y-1 text-sm">
          <li className="rounded bg-slate-100 px-2 py-1">{filename}</li>
        </ul>
        <h4 className="mt-4 text-sm font-semibold">Snapshots</h4>
        <ul className="mt-2 max-h-72 space-y-1 overflow-auto text-xs">
          {snapshots.map((snapshot) => (
            <li key={snapshot.id}>
              <button
                className="w-full rounded border px-2 py-1 text-left hover:bg-slate-50"
                onClick={() => {
                  setFilename(snapshot.filename)
                  setCode(snapshot.content)
                }}
              >
                {snapshot.filename} • {new Date(snapshot.created_at).toLocaleString()}
              </button>
            </li>
          ))}
        </ul>
      </section>

      <section className="space-y-3 rounded-xl border bg-white p-4 shadow-sm">
        <h2 className="text-xl font-bold">Code Lab</h2>
        <label className="text-sm">
          Filename
          <input value={filename} onChange={(e) => setFilename(e.target.value)} className="mt-1 w-full rounded border px-2 py-1" />
        </label>
        <textarea
          value={code}
          onChange={(e) => setCode(e.target.value)}
          className="h-72 w-full rounded border bg-slate-900 p-3 font-mono text-xs text-emerald-200"
        />
        <label className="text-sm">
          Public tests
          <textarea value={testsPublic} onChange={(e) => setTestsPublic(e.target.value)} className="mt-1 h-24 w-full rounded border p-2 font-mono text-xs" />
        </label>
        <div className="flex gap-2">
          <button className="rounded bg-brand-500 px-4 py-2 text-sm font-semibold text-white" onClick={runCode}>
            Run code
          </button>
          <button className="rounded bg-slate-200 px-4 py-2 text-sm font-semibold" onClick={saveSnapshot}>
            Save snapshot
          </button>
        </div>
        <pre className="min-h-24 whitespace-pre-wrap rounded border bg-slate-50 p-3 text-xs">{runOutput || 'Run output appears here.'}</pre>
      </section>
    </div>
  )
}
