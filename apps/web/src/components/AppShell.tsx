import { NavLink } from 'react-router-dom'

import { useAppContext } from '../context/AppContext'

const navItems = [
  { to: '/dashboard', label: 'Dashboard' },
  { to: '/learn', label: 'Learn' },
  { to: '/practice', label: 'Practice' },
  { to: '/exam-skills', label: 'Exam Skills' },
  { to: '/buddy', label: 'Buddy' },
  { to: '/tools/code-lab', label: 'Code Lab' },
  { to: '/tools/data-lab', label: 'Data Lab' },
  { to: '/quick-wins', label: 'Quick Wins' },
  { to: '/projects', label: 'Projects' },
  { to: '/profile', label: 'Profile' },
]

export function AppShell({ children }: { children: React.ReactNode }) {
  const { subjectCode, setSubjectCode, unit, setUnit, track } = useAppContext()

  return (
    <div className="min-h-screen bg-slate-50">
      <header className="border-b bg-white">
        <div className="mx-auto flex w-full max-w-7xl flex-wrap items-center justify-between gap-3 px-4 py-4">
          <div>
            <h1 className="text-xl font-bold text-slate-900">VCE Prep Buddy</h1>
            <p className="text-xs text-slate-500">VCE Applied Computing (Accredited 2025+)</p>
          </div>
          <div className="flex flex-wrap items-center gap-2 rounded-lg border bg-slate-50 p-2">
            <select
              value={subjectCode}
              onChange={(e) => setSubjectCode(e.target.value as 'SOFTDEV' | 'DATA')}
              className="rounded border px-2 py-1 text-sm"
            >
              <option value="SOFTDEV">Software Development</option>
              <option value="DATA">Data Analytics</option>
            </select>
            <select
              value={unit}
              onChange={(e) => setUnit(Number(e.target.value) as 1 | 2 | 3 | 4)}
              className="rounded border px-2 py-1 text-sm"
            >
              {[1, 2, 3, 4].map((value) => (
                <option key={value} value={value}>
                  Unit {value}
                </option>
              ))}
            </select>
            <span
              className={`rounded px-2 py-1 text-xs font-semibold ${
                track === 'foundation' ? 'bg-emerald-100 text-emerald-700' : 'bg-amber-100 text-amber-700'
              }`}
            >
              {track === 'foundation' ? 'Foundation Track' : 'Scored Track'}
            </span>
          </div>
        </div>
        <nav className="mx-auto flex w-full max-w-7xl flex-wrap gap-2 px-4 pb-4">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `rounded-md px-3 py-1.5 text-sm transition ${
                  isActive ? 'bg-brand-500 text-white' : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
                }`
              }
            >
              {item.label}
            </NavLink>
          ))}
          {unit >= 3 && (
            <NavLink
              to="/sat"
              className={({ isActive }) =>
                `rounded-md px-3 py-1.5 text-sm transition ${
                  isActive ? 'bg-brand-500 text-white' : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
                }`
              }
            >
              SAT Hub
            </NavLink>
          )}
        </nav>
      </header>
      <main className="mx-auto w-full max-w-7xl p-4">{children}</main>
    </div>
  )
}
