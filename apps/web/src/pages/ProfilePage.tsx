import { useQuery } from '@tanstack/react-query'

import { api } from '../lib/api'

interface Profile {
  id: number
  email: string
  role: string
  attempt_count: number
  average_mastery: number
}

export function ProfilePage() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['profile'],
    queryFn: () => api.get<Profile>('/api/profile'),
  })

  if (isLoading) return <p>Loading profile...</p>
  if (error) return <p className="text-rose-600">Failed to load profile.</p>

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-bold">Profile</h2>
      <section className="rounded-xl border bg-white p-4 shadow-sm">
        <p className="text-sm text-slate-500">Email</p>
        <p className="font-semibold">{data?.email}</p>
        <p className="mt-3 text-sm text-slate-500">Role</p>
        <p className="font-semibold capitalize">{data?.role}</p>
        <p className="mt-3 text-sm text-slate-500">Attempt count</p>
        <p className="font-semibold">{data?.attempt_count}</p>
        <p className="mt-3 text-sm text-slate-500">Average mastery</p>
        <p className="font-semibold">{Math.round((data?.average_mastery ?? 0) * 100)}%</p>
      </section>
    </div>
  )
}
