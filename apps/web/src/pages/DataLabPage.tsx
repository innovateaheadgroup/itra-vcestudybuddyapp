import { useState } from 'react'

import { api, getAccessToken } from '../lib/api'

interface UploadResponse {
  dataset_id: number
  filename: string
  columns: Record<string, string>
  preview_rows: Record<string, string | number>[]
  cleaning_suggestions: string[]
}

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

export function DataLabPage() {
  const [uploadData, setUploadData] = useState<UploadResponse | null>(null)
  const [chartConfig, setChartConfig] = useState('{\n  "type": "bar",\n  "x": "category",\n  "y": "value"\n}')
  const [insightDraft, setInsightDraft] = useState('')
  const [status, setStatus] = useState('')

  async function uploadCsv(file: File) {
    const formData = new FormData()
    formData.append('file', file)
    const response = await fetch(`${API_BASE_URL}/api/tools/data-lab/upload`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${getAccessToken()}`,
      },
      body: formData,
    })
    if (!response.ok) {
      throw new Error(await response.text())
    }
    const data = (await response.json()) as UploadResponse
    setUploadData(data)
  }

  async function saveChartConfig() {
    if (!uploadData) return
    const parsed = JSON.parse(chartConfig)
    await api.post('/api/tools/data-lab/chart-config', {
      dataset_id: uploadData.dataset_id,
      config_json: parsed,
    })
    setStatus('Chart config saved.')
  }

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-bold">Data Lab</h2>

      <section className="rounded-xl border bg-white p-4 shadow-sm">
        <h3 className="text-base font-semibold">Upload CSV</h3>
        <input
          type="file"
          accept=".csv"
          className="mt-2 text-sm"
          onChange={(event) => {
            const file = event.target.files?.[0]
            if (!file) return
            void uploadCsv(file)
          }}
        />
      </section>

      {uploadData && (
        <>
          <section className="rounded-xl border bg-white p-4 shadow-sm">
            <h3 className="text-base font-semibold">Table preview + inferred column types</h3>
            <p className="text-sm text-slate-500">{uploadData.filename}</p>
            <div className="mt-2 flex flex-wrap gap-2">
              {Object.entries(uploadData.columns).map(([column, dtype]) => (
                <span key={column} className="rounded bg-slate-100 px-2 py-1 text-xs">
                  {column}: {dtype}
                </span>
              ))}
            </div>
            <pre className="mt-3 overflow-auto rounded border bg-slate-50 p-3 text-xs">
              {JSON.stringify(uploadData.preview_rows, null, 2)}
            </pre>
          </section>

          <section className="rounded-xl border bg-white p-4 shadow-sm">
            <h3 className="text-base font-semibold">Cleaning suggestions</h3>
            <ul className="ml-4 list-disc text-sm">
              {uploadData.cleaning_suggestions.map((suggestion) => (
                <li key={suggestion}>{suggestion}</li>
              ))}
            </ul>
          </section>

          <section className="rounded-xl border bg-white p-4 shadow-sm">
            <h3 className="text-base font-semibold">Visualisation builder config</h3>
            <textarea
              value={chartConfig}
              onChange={(e) => setChartConfig(e.target.value)}
              className="h-36 w-full rounded border p-2 font-mono text-xs"
            />
            <button className="mt-2 rounded bg-brand-500 px-4 py-2 text-sm font-semibold text-white" onClick={saveChartConfig}>
              Save chart config
            </button>
            {status ? <p className="mt-1 text-xs text-emerald-700">{status}</p> : null}
          </section>

          <section className="rounded-xl border bg-white p-4 shadow-sm">
            <h3 className="text-base font-semibold">Insight writing panel</h3>
            <p className="text-xs text-slate-500">
              Template: Claim -&gt; Evidence -&gt; Explanation -&gt; Limitation
            </p>
            <textarea
              value={insightDraft}
              onChange={(e) => setInsightDraft(e.target.value)}
              className="mt-2 h-36 w-full rounded border p-2 text-sm"
              placeholder="Draft your insight..."
            />
            <div className="mt-2 flex items-center gap-2">
              <a href="/buddy" className="rounded bg-slate-200 px-3 py-1 text-xs font-semibold">
                Buddy review
              </a>
            </div>
          </section>
        </>
      )}
    </div>
  )
}
