/**
 * src/types/index.ts
 *
 * Shared TypeScript types matching the backend Pydantic schemas.
 */

// ── Generic API wrapper ─────────────────────────────────────────
export interface APIResponse<T> {
  success: boolean
  message: string
  data: T
}

// ── Auth ─────────────────────────────────────────────────────────
export interface LoginRequest {
  email: string
  password: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
  user: User
}

export interface User {
  id: string
  full_name: string
  email: string
  role: 'qa_engineer' | 'admin'
  is_active: boolean
  created_at: string
}

// ── Requirements ─────────────────────────────────────────────────
export type RequirementStatus =
  | 'submitted'
  | 'analyzing'
  | 'analyzed'
  | 'scenarios_ready'
  | 'test_cases_ready'
  | 'approved'
  | 'automation_generated'
  | 'completed'
  | 'failed'

export interface Requirement {
  id: string
  title: string
  description: string
  submitted_by: string | null
  status: RequirementStatus
  ai_analysis: Record<string, unknown> | null
  created_at: string
  updated_at: string
}

export interface RequirementCreate {
  title: string
  description: string
}

// ── Scenarios ────────────────────────────────────────────────────
export type ScenarioType = 'positive' | 'negative' | 'edge'
export type Priority = 'high' | 'medium' | 'low'

export interface TestScenario {
  id: string
  requirement_id: string
  scenario_title: string
  scenario_type: ScenarioType
  scenario_description: string
  priority: Priority
  generated_by_ai: boolean
  created_at: string
  test_cases?: TestCase[]
}

// ── Test Cases ───────────────────────────────────────────────────
export type TestCaseStatus = 'draft' | 'approved' | 'rejected'

export interface TestStep {
  step_number: number
  action: string
  expected: string
}

export interface TestCase {
  id: string
  scenario_id: string
  test_case_title: string
  preconditions: string | null
  test_steps: TestStep[]
  expected_result: string
  test_data: Record<string, string> | null
  priority: Priority
  status: TestCaseStatus
  created_at: string
  automation_script?: AutomationScript | null
}

// ── Automation Scripts ───────────────────────────────────────────
export interface AutomationScript {
  id: string
  test_case_id: string
  framework: string
  script_content: string
  script_filename: string
  github_commit_url: string | null
  github_branch: string | null
  generation_status: 'generated' | 'pushed' | 'failed'
  created_at: string
}

// ── Approvals ────────────────────────────────────────────────────
export interface ApprovalLog {
  id: string
  requirement_id: string
  approved_by: string
  approval_status: 'approved' | 'rejected' | 'regenerate'
  comments: string | null
  reviewed_at: string
}

// ── Workflow Executions ──────────────────────────────────────────
export interface WorkflowExecution {
  id: string
  workflow_name: string
  requirement_id: string | null
  execution_status: 'running' | 'success' | 'failed'
  started_at: string
  completed_at: string | null
  logs: string | null
  error_message: string | null
}

// ── Dashboard Stats ──────────────────────────────────────────────
export interface DashboardStats {
  total_requirements: number
  total_scenarios: number
  total_test_cases: number
  total_scripts_generated: number
  pending_approvals: number
  recent_requirements: Requirement[]
}
