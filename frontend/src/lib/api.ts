/**
 * src/lib/api.ts
 *
 * Axios instance pre-configured for QPilot API.
 * - Attaches JWT token to every request
 * - Handles 401 by redirecting to login
 * - Consistent error shape
 */

import axios, { AxiosError } from 'axios'

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export const api = axios.create({
  baseURL: `${API_BASE}/api/v1`,
  headers: { 'Content-Type': 'application/json' },
  timeout: 60_000,
})

// Attach token from localStorage
api.interceptors.request.use((config) => {
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('qpilot_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
  }
  return config
})

// Handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401 && typeof window !== 'undefined') {
      localStorage.removeItem('qpilot_token')
      window.location.href = '/auth/login'
    }
    return Promise.reject(error)
  }
)

// Typed helper to extract error message from API response
export function getErrorMessage(error: unknown): string {
  if (error instanceof AxiosError) {
    const data = error.response?.data as { message?: string } | undefined
    return data?.message ?? error.message ?? 'An unexpected error occurred.'
  }
  if (error instanceof Error) return error.message
  return 'An unexpected error occurred.'
}
