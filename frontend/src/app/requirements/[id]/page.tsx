'use client'

/**
 * src/app/requirements/[id]/page.tsx
 * Single requirement view — shows AI analysis, scenarios, test cases, approval
 */

import { useEffect, useState } from 'react'
import { useParams } from 'next/navigation'
import Link from 'next/link'
import {
  ArrowLeft, Bot, CheckCircle, XCircle, RefreshCw,
  ChevronDown, ChevronRight, Code2, Loader2, Zap
} from 'lucide-react'
import { toast } from 'sonner'
import { requirementsService, scenariosService, testCasesService, approvalsService } from '@/services'
import type { Requirement, TestScenario, TestCase } from '@/types'
import { getErrorMessage } from '@/lib/api'

const PRIORITY_BADGE: Record<string, string> = {
  high: 'badge-red', medium: 'badge-yellow', low: 'badge-gray'
}
const TYPE_BADGE: Record<string, string> = {
  positive: 'badge-green', negative: 'badge-red', edge: 'badge-purple'
}

function ScenarioCard({ scenario }: { scenario: TestScenario }) {
  const [expanded, setExpanded] = useState(false)
  const [testCases, setTestCases] = useState<TestCase[]>([])
  const [isLoadingCases, setIsLoadingCases] = useState(false)
  const [isGenerating, setIsGenerating] = useState(false)

  const loadTestCases = async () => {
    setIsLoadingCases(true)
    try {
      const cases = await testCasesService.list(scenario.id)
      setTestCases(cases)
    } finally {
      setIsLoadingCases(false)
    }
  }

  const handleExpand = () => {
    if (!expanded) loadTestCases()
    setExpanded(!expanded)
  }

  const handleGenerate = async (e: React.MouseEvent) => {
    e.stopPropagation()
    setIsGenerating(true)
    try {
      const cases = await testCasesService.generate(scenario.id)
      setTestCases(cases)
      setExpanded(true)
      toast.success(`Generated ${cases.length} test cases`)
    } catch (error) {
      toast.error(getErrorMessage(error))
    } finally {
      setIsGenerating(false)
    }
  }

  return (
    <div className="border border-gray-200 rounded-lg overflow-hidden">
      <div
        className="flex items-center gap-3 p-4 cursor-pointer hover:bg-gray-50"
        onClick={handleExpand}
      >
        {expanded ? <ChevronDown className="w-4 h-4 text-gray-400" /> : <ChevronRight className="w-4 h-4 text-gray-400" />}
        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium text-gray-900">{scenario.scenario_title}</p>
          <p className="text-xs text-gray-500 mt-0.5 truncate">{scenario.scenario_description}</p>
        </div>
        <div className="flex items-center gap-2 flex-shrink-0">
          <span className={TYPE_BADGE[scenario.scenario_type] ?? 'badge-gray'}>{scenario.scenario_type}</span>
          <span className={PRIORITY_BADGE[scenario.priority] ?? 'badge-gray'}>{scenario.priority}</span>
          <button
            onClick={handleGenerate}
            disabled={isGenerating}
            className="text-brand-600 text-xs hover:underline flex items-center gap-1 ml-2"
          >
            {isGenerating ? <Loader2 className="w-3 h-3 animate-spin" /> : <Zap className="w-3 h-3" />}
            Generate cases
          </button>
        </div>
      </div>

      {expanded && (
        <div className="border-t border-gray-100 bg-gray-50 p-4">
          {isLoadingCases ? (
            <div className="flex items-center gap-2 text-gray-400 text-sm">
              <Loader2 className="w-4 h-4 animate-spin" /> Loading test cases...
            </div>
          ) : testCases.length === 0 ? (
            <p className="text-sm text-gray-400">No test cases yet. Click "Generate cases" to create them.</p>
          ) : (
            <div className="space-y-3">
              {testCases.map((tc) => (
                <div key={tc.id} className="bg-white rounded-lg p-3 border border-gray-200">
                  <div className="flex items-center justify-between mb-2">
                    <p className="text-sm font-medium text-gray-800">{tc.test_case_title}</p>
                    <span className={PRIORITY_BADGE[tc.priority] ?? 'badge-gray'}>{tc.priority}</span>
                  </div>
                  {tc.preconditions && (
                    <p className="text-xs text-gray-500 mb-2"><strong>Preconditions:</strong> {tc.preconditions}</p>
                  )}
                  <div className="space-y-1">
                    {(Array.isArray(tc.test_steps) ? tc.test_steps : []).map((step) => (
                      <div key={step.step_number} className="text-xs text-gray-600 flex gap-2">
                        <span className="font-mono text-gray-400 flex-shrink-0">{step.step_number}.</span>
                        <span>{step.action}</span>
                      </div>
                    ))}
                  </div>
                  <p className="text-xs text-green-700 mt-2 font-medium">✓ {tc.expected_result}</p>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default function RequirementDetailPage() {
  const params = useParams()
  const id = params.id as string
  const [req, setReq] = useState<Requirement | null>(null)
  const [scenarios, setScenarios] = useState<TestScenario[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [isGeneratingScenarios, setIsGeneratingScenarios] = useState(false)
  const [isApproving, setIsApproving] = useState<string | null>(null)

  useEffect(() => {
    Promise.all([
      requirementsService.get(id),
      scenariosService.list(id).catch(() => []),
    ]).then(([requirement, scens]) => {
      setReq(requirement)
      setScenarios(scens)
    }).finally(() => setIsLoading(false))
  }, [id])

  const handleGenerateScenarios = async () => {
    setIsGeneratingScenarios(true)
    try {
      const scens = await scenariosService.generate(id)
      setScenarios(scens)
      toast.success(`Generated ${scens.length} test scenarios!`)
    } catch (error) {
      toast.error(getErrorMessage(error))
    } finally {
      setIsGeneratingScenarios(false)
    }
  }

  const handleApproval = async (status: 'approved' | 'rejected' | 'regenerate', comments?: string) => {
    setIsApproving(status)
    try {
      await approvalsService.approve({ requirement_id: id, approval_status: status, comments })
      toast.success(status === 'approved' ? 'Approved! Automation pipeline starting...' : 'Action recorded.')
      const updated = await requirementsService.get(id)
      setReq(updated)
    } catch (error) {
      toast.error(getErrorMessage(error))
    } finally {
      setIsApproving(null)
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader2 className="w-8 h-8 text-brand-500 animate-spin" />
      </div>
    )
  }

  if (!req) return <div className="p-8 text-gray-500">Requirement not found.</div>

  const analysis = req.ai_analysis as Record<string, unknown> | null

  return (
    <div className="p-8 max-w-4xl mx-auto animate-fade-in">
      {/* Back */}
      <Link href="/requirements" className="flex items-center gap-1 text-sm text-gray-500 hover:text-gray-700 mb-6">
        <ArrowLeft className="w-4 h-4" /> Back to requirements
      </Link>

      {/* Header */}
      <div className="card p-6 mb-6">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <h1 className="text-xl font-bold text-gray-900">{req.title}</h1>
            <p className="text-gray-500 text-sm mt-2 leading-relaxed">{req.description}</p>
          </div>
          <span className="badge-blue ml-4 flex-shrink-0">{req.status.replace(/_/g, ' ')}</span>
        </div>
      </div>

      {/* AI Analysis */}
      {analysis && (
        <div className="card p-6 mb-6">
          <div className="flex items-center gap-2 mb-4">
            <Bot className="w-5 h-5 text-brand-600" />
            <h2 className="font-semibold text-gray-900">AI Analysis</h2>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {['testing_areas', 'potential_risks', 'edge_cases', 'validation_points'].map((key) => {
              const items = analysis[key] as string[] | undefined
              if (!items?.length) return null
              return (
                <div key={key}>
                  <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-2">
                    {key.replace(/_/g, ' ')}
                  </p>
                  <ul className="space-y-1">
                    {items.map((item, i) => (
                      <li key={i} className="text-xs text-gray-600 flex gap-2">
                        <span className="text-brand-400 flex-shrink-0">•</span>
                        {item}
                      </li>
                    ))}
                  </ul>
                </div>
              )
            })}
          </div>
        </div>
      )}

      {/* Scenarios */}
      <div className="card p-6 mb-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="font-semibold text-gray-900">
            Test Scenarios
            {scenarios.length > 0 && (
              <span className="ml-2 text-sm text-gray-400 font-normal">({scenarios.length})</span>
            )}
          </h2>
          {scenarios.length === 0 && (
            <button
              onClick={handleGenerateScenarios}
              disabled={isGeneratingScenarios}
              className="btn-primary flex items-center gap-2"
            >
              {isGeneratingScenarios ? (
                <><Loader2 className="w-4 h-4 animate-spin" /> Generating...</>
              ) : (
                <><Zap className="w-4 h-4" /> Generate Scenarios</>
              )}
            </button>
          )}
        </div>

        {scenarios.length === 0 ? (
          <p className="text-sm text-gray-400">No scenarios yet. Click "Generate Scenarios" to start.</p>
        ) : (
          <div className="space-y-3">
            {scenarios.map((s) => <ScenarioCard key={s.id} scenario={s} />)}
          </div>
        )}
      </div>

      {/* Approval Panel */}
      {scenarios.length > 0 && req.status === 'test_cases_ready' && (
        <div className="card p-6 border-2 border-brand-200 bg-brand-50">
          <h2 className="font-semibold text-gray-900 mb-1">QA Review & Approval</h2>
          <p className="text-sm text-gray-600 mb-4">
            Review the generated scenarios and test cases. Once approved, the automation pipeline will:
            generate Playwright scripts → push to GitHub → create Jira tickets → notify the team.
          </p>
          <div className="flex items-center gap-3">
            <button
              onClick={() => handleApproval('approved')}
              disabled={!!isApproving}
              className="btn-primary flex items-center gap-2"
            >
              {isApproving === 'approved' ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <CheckCircle className="w-4 h-4" />
              )}
              Approve & Run Pipeline
            </button>
            <button
              onClick={() => handleApproval('regenerate')}
              disabled={!!isApproving}
              className="btn-secondary flex items-center gap-2"
            >
              <RefreshCw className="w-4 h-4" /> Regenerate
            </button>
            <button
              onClick={() => handleApproval('rejected')}
              disabled={!!isApproving}
              className="btn-danger flex items-center gap-2"
            >
              <XCircle className="w-4 h-4" /> Reject
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
