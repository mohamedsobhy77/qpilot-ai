/**
 * src/store/auth.ts
 *
 * Zustand store for authentication state.
 * Persists token in localStorage; user object in memory.
 */

import { create } from 'zustand'
import type { User } from '@/types'

interface AuthState {
  token: string | null
  user: User | null
  isAuthenticated: boolean
  setAuth: (token: string, user: User) => void
  clearAuth: () => void
}

export const useAuthStore = create<AuthState>((set) => ({
  token: typeof window !== 'undefined' ? localStorage.getItem('qpilot_token') : null,
  user: null,
  isAuthenticated: typeof window !== 'undefined' ? !!localStorage.getItem('qpilot_token') : false,

  setAuth: (token, user) => {
    if (typeof window !== 'undefined') {
      localStorage.setItem('qpilot_token', token)
    }
    set({ token, user, isAuthenticated: true })
  },

  clearAuth: () => {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('qpilot_token')
    }
    set({ token: null, user: null, isAuthenticated: false })
  },
}))
