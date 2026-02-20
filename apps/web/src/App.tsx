import { useEffect, useState } from 'react'

import { Navigate, Route, Routes } from 'react-router-dom'

import { AppShell } from './components/AppShell'
import { AppProvider } from './context/AppContext'
import { ensureDemoAuth } from './lib/api'
import { BuddyPage } from './pages/BuddyPage'
import { CodeLabPage } from './pages/CodeLabPage'
import { DashboardPage } from './pages/DashboardPage'
import { DataLabPage } from './pages/DataLabPage'
import { ExamSkillsPage } from './pages/ExamSkillsPage'
import { LearnPage } from './pages/LearnPage'
import { NotFoundPage } from './pages/NotFoundPage'
import { PracticePage } from './pages/PracticePage'
import { ProfilePage } from './pages/ProfilePage'
import { ProjectsPage } from './pages/ProjectsPage'
import { QuickWinsPage } from './pages/QuickWinsPage'
import { SatHubPage } from './pages/SatHubPage'

function App() {
  const [ready, setReady] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    ensureDemoAuth()
      .then(() => setReady(true))
      .catch((err) => {
        setError(String(err))
      })
  }, [])

  if (error) {
    return (
      <div className="mx-auto mt-10 max-w-xl rounded border border-rose-200 bg-rose-50 p-4 text-sm text-rose-700">
        Authentication bootstrap failed: {error}
      </div>
    )
  }
  if (!ready) {
    return <p className="p-4 text-sm text-slate-500">Preparing VCE Prep Buddy...</p>
  }

  return (
    <AppProvider>
      <AppShell>
        <Routes>
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/learn" element={<LearnPage />} />
          <Route path="/practice" element={<PracticePage />} />
          <Route path="/exam-skills" element={<ExamSkillsPage />} />
          <Route path="/buddy" element={<BuddyPage />} />
          <Route path="/tools/code-lab" element={<CodeLabPage />} />
          <Route path="/tools/data-lab" element={<DataLabPage />} />
          <Route path="/quick-wins" element={<QuickWinsPage />} />
          <Route path="/sat" element={<SatHubPage />} />
          <Route path="/projects" element={<ProjectsPage />} />
          <Route path="/profile" element={<ProfilePage />} />
          <Route path="*" element={<NotFoundPage />} />
        </Routes>
      </AppShell>
    </AppProvider>
  )
}

export default App
