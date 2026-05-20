'use client'

/**
 * src/app/scenarios/page.tsx
 *
 * All test scenarios grouped by requirement.
 * Each scenario row can be expanded to reveal its test cases.
 */

import { useEffect, useState } from 'react'
import Link from 'next/link'
import {
  FlaskConical, ChevronDown, ChevronRight,
  Loader2, AlertCircle, Zap,
} from 'lucide-react'
import { toast } from 'sonner'
import { requirementsService, scenariosService, testCasesService } from '@/services'
import type { Requirement, TestScenario, TestCase } from '@/types'
import { getErrorMessage } from '@/lib/api'
import { clsx } from 'clsx'

const TYPE_BADGE: Record<string, string> = {
  positive: 'badge-green', negative: 'badge-red', edge: 'badge-purple',
}
const PRIORITY_BADGE: Record<string, string> = {
  high: 'badge-red', medium: 'badge-yellow', low: 'badge-gray',
}

// ── Single test case row ──────────────────────────────────────────
function TestCaseRow({ tc }: { tc: TestCase }) {
  const steps = Array.isArray(tc.test_steps) ? tc.test_steps : []
  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4">
      <div className="flex items-start justify-between gap-4 mb-3">
        <p className="text-sm font-medium text-gray-800">{tc.test_case_title}</p>
        <span className={PRIORITY_BADGE[tc.priority] ?? 'badge-gray'}>{tc.priority}</span>
      </div>
      {tc.preconditions && (
        <p className="text-xs text-gray-500 mb-3">
          <span className="font-semibold text-gray-600">Preconditions: </span>
          {tc.preconditions}
        </p>
      )}
      <ol className="space-y-1.5 mb-3">
        {steps.map((step) => (
          <li key={step.step_number} className="flex gap-2 text-xs text-gray-600">
            <span className="font-mono text-gray-400 w-4 flex-shrink-0">{step.step_number}.</span>
            <div>
              <span>{step.action}</span>
              {step.expected && (
                <span className="text-gray-400 ml-1">→ {step.expected}</span>
              )}
            </div>
          </li>
        ))}
      </ol>
      <p className="text-xs font-medium text-green-700">
        ✓ Expected: {tc.expected_result}
      </p>
    </div>
  )
}

// ── Single scenario row with expandable test cases ─────────────────
function ScenarioRow({ scenario }: { scenario: TestScenario }) {
  const [open, setOpen] = useState(false)
  const [cases, setCases] = useState<TestCase[]>([])
  const [loading, setLoading] = useState(false)
  const [generating, setGenerating] = useState(false)
  const [loaded, setLoaded] = useState(false)

  const handleToggle = async () => {
    if (!open && !loaded) {
      setLoading(true)
      try {
        const data = await testCasesService.list(scenario.id)
        setCases(data)
        setLoaded(true)
      } catch {
        toast.error('Failed to load test cases.')
      } finally {
        setLoading(false)
      }
    }
    setOpen(!open)
  }

  const handleGenerate = async (e: React.MouseEvent) => {
    e.stopPropagation()
    setGenerating(true)
    try {
      const data = await testCasesService.generate(scenario.id)
      setCases(data)
      setLoaded(true)
      setOpen(true)
      toast.success(`Generated ${data.length} test cases`)
    } catch (error) {
      toast.error(getErrorMessage(error))
    } finally {
      setGenerating(false)
    }
  }

  return (
    <div className="border border-gray-200 rounded-lg overflow-hidden">
      <div
        className="flex items-center gap-3 p-4 cursor-pointer hover:bg-gray-50 transition-colors"
        onClick={handleToggle}
      >
        {open
          ? <ChevronDown className="w-4 h-4 text-gray-400 flex-shrink-0" />
          : <ChevronRight className="w-4 h-4 text-gray-400 flex-shrink-0" />
        }
        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium text-gray-900 truncate">{scenario.scenario_title}</p>
          <p className="text-xs text-gray-500 mt-0.5 line-clamp-1">{scenario.scenario_description}</p>
        </div>
        <div className="flex items-center gap-2 flex-shrink-0">
          <span className={TYPE_BADGE[scenario.scenario_type] ?? 'badge-gray'}>
            {scenario.scenario_type}
          </span>
          <span className={PRIORITY_BADGE[scenario.priority] ?? 'badge-gray'}>
            {scenario.priority}
          </span>
          <button
            onClick={handleGenerate}
            disabled={generating}
            className="flex items-center gap-1 text-xs text-brand-600 hover:text-brand-700 font-medium ml-2 disabled:opacity-50"
          >
            {generating
              ? <Loader2 className="w-3 h-3 animate-spin" />
              : <Zap className="w-3 h-3" />
            }
            {cases.length > 0 ? 'Regen' : 'Generate'}
          </button>
        </div>
      </div>

      {open && (
        <div className="border-t border-gray-100 bg-gray-50 p-4">
          {loading ? (
            <div className="flex items-center gap-2 text-gray-400 text-sm py-2">
              <Loader2 className="w-4 h-4 animate-spin" /> Loading test cases...
            </div>
          ) : cases.length === 0 ? (
            <p className="text-sm text-gray-400 py-2">
              No test cases yet. Click{' '}
              <button onClick={handleGenerate} className="text-brand-600 hover:underline">
                Generate
              </button>{' '}
              to create them with AI.
            </p>
          ) : (
            <div className="space-y-3">
              {cases.map(tc => <TestCaseRow key={tc.id} tc={tc} />)}
            </div>
          )}
        </div>
      )}
    </div>
  )
}

// ── Requirement group ─────────────────────────────────────────────
function RequirementGroup({ req }: { req: Requirement }) {
  const [scenarios, setScenarios] = useState<TestScenario[]>([])
  const [open, setOpen] = useState(false)
  const [loading, setLoading] = useState(false)
  const [loaded, setLoaded] = useState(false)

  const handleToggle = async () => {
    if (!open && !loaded) {
      setLoading(true)
      try {
        const data = await scenariosService.list(req.id)
        setScenarios(data)
        setLoaded(true)
      } catch {
        toast.error('Failed to load scenarios.')
      } finally {
        setLoading(false)
      }
    }
    setOpen(!open)
  }

  return (
    <div className="card overflow-hidden mb-4">
      <div
        className="flex items-center gap-3 p-5 cursor-pointer hover:bg-gray-50 transition-colors"
        onClick={handleToggle}
      >
        {open
          ? <ChevronDown className="w-5 h-5 text-gray-400 flex-shrink-0" />
          : <ChevronRight className="w-5 h-5 text-gray-400 flex-shrink-0" />
        }
        <div className="flex-1 min-w-0">
          <p className="font-semibold text-gray-900">{req.title}</p>
          <p className="text-sm text-gray-400 mt-0.5">
            {new Date(req.created_at).toLocaleDateString('en-US', {
              month: 'short', day: 'numeric', year: 'numeric',
            })}
          </p>
        </div>
        <Link
          href={`/requirements/${req.id}`}
          onClick={e => e.stopPropagation()}
          className="text-xs text-brand-600 hover:underline mr-2"
        >
          View requirement →
        </Link>
        {loading && <Loader2 className="w-4 h-4 text-gray-400 animate-spin" />}
      </div>

      {open && (
        <div className="border-t border-gray-100 p-5">
          {scenarios.length === 0 ? (
            <p className="text-sm text-gray-400">
              No scenarios for this requirement.{' '}
              <Link href={`/requirements/${req.id}`} className="text-brand-600 hover:underline">
                Generate from requirement page →
              </Link>
            </p>
          ) : (
            <div className="space-y-3">
              {scenarios.map(s => <ScenarioRow key={s.id} scenario={s} />)}
            </div>
          )}
        </div>
      )}
    </div>
  )
}

// ── Page ──────────────────────────────────────────────────────────
export default function ScenariosPage() {
  const [requirements, setRequirements] = useState<Requirement[]>([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    requirementsService.list(0, 50)
      .then(d => setRequirements(d.requirements))
      .catch(() => toast.error('Failed to load requirements.'))
      .finally(() => setIsLoading(false))
  }, [])

  return (
    <div className="p-8 max-w-5xl mx-auto animate-fade-in">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Test Scenarios</h1>
        <p className="text-gray-500 text-sm mt-1">
          All AI-generated scenarios grouped by requirement. Expand to view and generate test cases.
        </p>
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center py-20">
          <Loader2 className="w-8 h-8 text-brand-500 animate-spin" />
        </div>
      ) : requirements.length === 0 ? (
        <div className="card flex flex-col items-center py-16 text-center">
          <FlaskConical className="w-12 h-12 text-gray-300 mb-4" />
          <h3 className="font-semibold text-gray-700 mb-1">No scenarios yet</h3>
          <p className="text-gray-400 text-sm mb-4">
            Submit a requirement and generate scenarios to see them here.
          </p>
          <Link href="/requirements" className="btn-primary">
            Go to Requirements
          </Link>
        </div>
      ) : (
        <div>
          <p className="text-sm text-gray-500 mb-4">
            Click a requirement to expand its scenarios.
          </p>
          {requirements.map(req => (
            <RequirementGroup key={req.id} req={req} />
          ))}
        </div>
      )}
    </div>
  )
}
