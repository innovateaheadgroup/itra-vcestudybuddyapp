import { Link } from 'react-router-dom'

export function NotFoundPage() {
  return (
    <div className="rounded-xl border bg-white p-6 text-center shadow-sm">
      <h2 className="text-xl font-bold">Page not found</h2>
      <p className="mt-2 text-sm text-slate-500">Use the navigation menu to return to a module.</p>
      <Link to="/dashboard" className="mt-4 inline-block rounded bg-brand-500 px-4 py-2 text-sm font-semibold text-white">
        Go to dashboard
      </Link>
    </div>
  )
}
