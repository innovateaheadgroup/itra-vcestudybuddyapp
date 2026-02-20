import type { FeedbackObject } from '@vce-prep-buddy/shared'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'
const TOKEN_KEY = 'vce_prep_buddy_access_token'
const REFRESH_KEY = 'vce_prep_buddy_refresh_token'

type HttpMethod = 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE'

export function getAccessToken() {
  return localStorage.getItem(TOKEN_KEY)
}

export function setTokens(access: string, refresh: string) {
  localStorage.setItem(TOKEN_KEY, access)
  localStorage.setItem(REFRESH_KEY, refresh)
}

async function request<T>(path: string, method: HttpMethod = 'GET', body?: unknown): Promise<T> {
  const token = getAccessToken()
  const headers: Record<string, string> = { 'Content-Type': 'application/json' }
  if (token) {
    headers.Authorization = `Bearer ${token}`
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  })

  if (response.status === 401 && localStorage.getItem(REFRESH_KEY)) {
    const refreshed = await tryRefreshToken()
    if (refreshed) {
      return request<T>(path, method, body)
    }
  }

  if (!response.ok) {
    const message = await response.text()
    throw new Error(message || `API request failed: ${response.status}`)
  }
  return response.json() as Promise<T>
}

async function tryRefreshToken() {
  const refresh = localStorage.getItem(REFRESH_KEY)
  if (!refresh) return false
  const response = await fetch(`${API_BASE_URL}/api/auth/refresh`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh_token: refresh }),
  })
  if (!response.ok) return false
  const data = (await response.json()) as { access_token: string; refresh_token: string }
  setTokens(data.access_token, data.refresh_token)
  return true
}

export async function ensureDemoAuth() {
  const token = getAccessToken()
  if (token) return

  try {
    const login = await request<{ access_token: string; refresh_token: string }>(
      '/api/auth/login',
      'POST',
      { email: 'student@example.com', password: 'ChangeMe123!' },
    )
    setTokens(login.access_token, login.refresh_token)
    return
  } catch {
    // try register fallback then login.
  }

  await request('/api/auth/register', 'POST', {
    email: 'student@example.com',
    password: 'ChangeMe123!',
    role: 'student',
  })
  const login = await request<{ access_token: string; refresh_token: string }>('/api/auth/login', 'POST', {
    email: 'student@example.com',
    password: 'ChangeMe123!',
  })
  setTokens(login.access_token, login.refresh_token)
}

export const api = {
  get: <T>(path: string) => request<T>(path, 'GET'),
  post: <T>(path: string, body?: unknown) => request<T>(path, 'POST', body),
}

export interface TopicCard {
  topic: {
    id: number
    subject_id: number
    unit: number
    aos: string
    outcome: string
    title: string
    order: number
    key_skills_json: Record<string, unknown>
  }
  mastery_pct: number
  status: 'Not started' | 'Learning' | 'Practising' | 'Ready'
  estimated_time: number
}

export interface Question {
  id: number
  topic_id: number
  type: string
  exam_style: string
  command_terms: string[]
  marks: number
  difficulty: number
  prompt_md: string
  case_material_md?: string | null
  options_json?: Record<string, string> | null
  starter_code?: string | null
}

export interface MarkResponse {
  feedback: FeedbackObject
  where_marks_were_lost: string[]
  common_mistakes: string[]
  upgrade_response: Record<string, unknown>
}
