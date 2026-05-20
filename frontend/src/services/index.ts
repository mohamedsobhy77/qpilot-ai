/**
 * src/services/index.ts
 *
 * All API call functions organized by domain.
 * Used by React Query hooks and page components.
 */

import { api } from '@/lib/api'
import type {
  APIResponse,
  DashboardStats,
  LoginRequest,
  LoginResponse,
  Requirement,
  RequirementCreate,
  TestScenario,
  TestCase,
  AutomationScript,
} from '@/types'

// ── Auth ─────────────────────────────────────────────────────────
export const authService = {
  async login(data: LoginRequest): Promise<LoginResponse> {
    const res = await api.post<LoginResponse>(
      '/auth/login',
      {
        email: data.email,
        password: data.password,
      },
      {
        headers: {
          'Content-Type': 'application/json',
        },
      }
    )

    return res.data
  },

  async getProfile() {
    const res = await api.get<APIResponse<{ user: LoginResponse['user'] }>>('/auth/profile')
    return res.data.data.user
  },
}


// ── Requirements ─────────────────────────────────────────────────
export const requirementsService = {
  async create(data: RequirementCreate): Promise<Requirement> {
    const res = await api.post<APIResponse<Requirement>>('/requirements', data)
    return res.data.data
  },

  async list(skip = 0, limit = 20): Promise<{ requirements: Requirement[]; total: number }> {
    const res = await api.get<APIResponse<{ requirements: Requirement[]; total: number }>>(
      `/requirements?skip=${skip}&limit=${limit}`
    )
    return res.data.data
  },

  async get(id: string): Promise<Requirement> {
    const res = await api.get<APIResponse<Requirement>>(`/requirements/${id}`)
    return res.data.data
  },
}

// ── Scenarios ─────────────────────────────────────────────────────
export const scenariosService = {
  async generate(requirementId: string): Promise<TestScenario[]> {
    const res = await api.post<APIResponse<{ scenarios: TestScenario[] }>>('/scenarios/generate', {
      requirement_id: requirementId,
    })
    return res.data.data.scenarios
  },

  async list(requirementId: string): Promise<TestScenario[]> {
    const res = await api.get<APIResponse<{ scenarios: TestScenario[] }>>(
      `/scenarios/${requirementId}`
    )
    return res.data.data.scenarios
  },
}

// ── Test Cases ────────────────────────────────────────────────────
export const testCasesService = {
  async generate(scenarioId: string): Promise<TestCase[]> {
    const res = await api.post<APIResponse<{ test_cases: TestCase[] }>>('/test-cases/generate', {
      scenario_id: scenarioId,
    })
    return res.data.data.test_cases
  },

  async list(scenarioId: string): Promise<TestCase[]> {
    const res = await api.get<APIResponse<{ test_cases: TestCase[] }>>(
      `/test-cases/${scenarioId}`
    )
    return res.data.data.test_cases
  },
}

// ── Approvals ─────────────────────────────────────────────────────
export const approvalsService = {
  async approve(data: {
    requirement_id: string
    approval_status: 'approved' | 'rejected' | 'regenerate'
    comments?: string
  }) {
    const res = await api.post<APIResponse<unknown>>('/approvals', data)
    return res.data
  },
}

// ── Automation ────────────────────────────────────────────────────
export const automationService = {
  async generate(testCaseId: string): Promise<AutomationScript> {
    const res = await api.post<APIResponse<AutomationScript>>('/automation/generate', {
      test_case_id: testCaseId,
      framework: 'playwright',
    })
    return res.data.data
  },

  async get(scriptId: string): Promise<AutomationScript> {
    const res = await api.get<APIResponse<AutomationScript>>(`/automation/${scriptId}`)
    return res.data.data
  },
}

// ── Dashboard ─────────────────────────────────────────────────────
export const dashboardService = {
  async getStats(): Promise<DashboardStats> {
    const res = await api.get<APIResponse<DashboardStats>>('/dashboard/stats')
    return res.data.data
  },
}
