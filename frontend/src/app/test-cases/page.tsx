'use client'

/**
 * src/app/test-cases/page.tsx
 *
 * Flat view of all test cases with:
 * - Status filter (draft / approved / rejected)
 * - Inline Playwright script viewer
 * - Generate script button per test case
 */

import { useEffect, useState } from 'react'
import {
  ClipboardList, Code2, Loader2, X,
  ChevronDown, ChevronRight, Zap,
} from 'lucide-react'
import Link from 'next/link'
import { toast } from 'sonner'
import { requirementsService, scenariosService, testCasesService, automationService } from '@/services'
import type { AutomationScript, Requirement, TestCase, TestScenario } from '@/types'
import { getErrorMessage } from '@/lib/api'
import { clsx } from 'clsx'

const PRIORITY_BADGE: Record<string, string> = {
  high: 'badge-red', medium: 'badge-yellow', low: 'badge-gray',
}
const STATUS_BADGE: Record<string, string> = {
  draft: 'badge-gray', approved: 'badge-green', rejected: 'badge-red',
}

// ── Script modal ───────────────────────────────────────────────────
function ScriptModal({ script, onClose }: { script: AutomationScript; onClose: () => void }) {
  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4">
      <div className="bg-gray-900 rounded-xl w-full max-w-3xl max-h-[80vh] flex flex-col">
        <div className="flex items-center justify-between px-5 py-4 border-b border-gray-700">
          <div>
            <p className="text-white font-semibold text-sm">{script.script_filename}</p>
            {script.github_commit_url && (
              <a
                href={script.github_commit_url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-brand-400 text-xs hover:underline"
              >
                View on GitHub →
              </a>
            )}
          </div>
          <button onClick={onClose} className="text-gray-400 hover:text-white transition-colors">
            <X className="w-5 h-5" />
          </button>
        </div>
        <div className="overflow-auto flex-1 p-5">
          <pre className="text-sm text-gray-100 whitespace-pre-wrap font-mono leading-relaxed">
            {script.script_content}
          </pre>
        </div>
      </div>
    </div>
  )
}

// ── Test case card ─────────────────────────────────────────────────
function TestCaseCard({ tc, scenarioTitle }: { tc: TestCase; scenarioTitle: string }) {
  const [open, setOpen] = useState(false)
  const [generating, setGenerating] = useState(false)
  const [script, setScript] = useState<AutomationScript | null>(tc.automation_script ?? null)
  const [showScript, setShowScript] = useState(false)
  const steps = Array.isArray(tc.test_steps) ? tc.test_steps : []

  const handleGenerateScript = async (e: React.MouseEvent) => {
    e.stopPropagation()
    setGenerating(true)
    try {
      const result = await automationService.generate(tc.id)
      setScript(result)
      toast.success('Playwright script generated!')
    } catch (error) {
      toast.error(getErrorMessage(error))
    } finally {
      setGenerating(false)
    }
  }

  return (
    <>
      <div className="card overflow-hidden">
        {/* Header */}
        <div
          className="flex items-start gap-3 p-5 cursor-pointer hover:bg-gray-50 transition-colors"
          onClick={() => setOpen(!open)}
        >
          {open
            ? <ChevronDown className="w-4 h-4 text-gray-400 flex-shrink-0 mt-0.5" />
            : <ChevronRight className="w-4 h-4 text-gray-400 flex-shrink-0 mt-0.5" />
          }
          <div className="flex-1 min-w-0">
            <p className="font-medium text-gray-900 text-sm">{tc.test_case_title}</p>
            <p className="text-xs text-gray-400 mt-0.5">Scenario: {scenarioTitle}</p>
          </div>
          <div className="flex items-center gap-2 flex-shrink-0">
            <span className={STATUS_BADGE[tc.status] ?? 'badge-gray'}>{tc.status}</span>
            <span className={PRIORITY_BADGE[tc.priority] ?? 'badge-gray'}>{tc.priority}</span>
          </div>
        </div>

        {/* Expanded body */}
        {open && (
          <div className="border-t border-gray-100 p-5 space-y-4">
            {tc.preconditions && (
              <div>
                <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1">Preconditions</p>
                <p className="text-sm text-gray-700">{tc.preconditions}</p>
              </div>
            )}
            <div>
              <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">Steps</p>
              <ol className="space-y-2">
                {steps.map(step => (
                  <li key={step.step_number} className="flex gap-3 text-sm">
                    <span className="flex-shrink-0 w-6 h-6 rounded-full bg-brand-100 text-brand-700 flex items-center justify-center text-xs font-bold">
                      {step.step_number}
                    </span>
                    <div className="pt-0.5">
                      <span className="text-gray-800">{step.action}</span>
                      {step.expected && (
                        <p className="text-xs text-gray-400 mt-0.5">→ {step.expected}</p>
                      )}
                    </div>
                  </li>
                ))}
              </ol>
            </div>
            <div>
              <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1">Expected Result</p>
              <p className="text-sm text-green-700 font-medium">{tc.expected_result}</p>
            </div>

            {/* Script actions */}
            <div className="flex items-center gap-3 pt-2 border-t border-gray-100">
              {script ? (
                <>
                  <button
                    onClick={() => setShowScript(true)}
                    className="btn-secondary flex items-center gap-2 text-sm"
                  >
                    <Code2 className="w-4 h-4" /> View Script
                  </button>
                  <button
                    onClick={handleGenerateScript}
                    disabled={generating}
                    className="text-xs text-gray-500 hover:text-gray-700 flex items-center gap-1"
                  >
                    {generating ? <Loader2 className="w-3 h-3 animate-spin" /> : <Zap className="w-3 h-3" />}
                    Regenerate
                  </button>
                </>
              ) : (
                <button
                  onClick={handleGenerateScript}
                  disabled={generating}
                  className="btn-primary flex items-center gap-2 text-sm"
                >
                  {generating
                    ? <><Loader2 className="w-4 h-4 animate-spin" /> Generating...</>
                    : <><Zap className="w-4 h-4" /> Generate Playwright Script</>
                  }
                </button>
              )}
            </div>
          </div>
        )}
      </div>

      {showScript && script && (
        <ScriptModal script={script} onClose={() => setShowScript(false)} />
      )}
    </>
  )
}

// ── Page ──────────────────────────────────────────────────────────
type FilterStatus = 'all' | 'draft' | 'approved' | 'rejected'

interface FlatTestCase extends TestCase {
  scenarioTitle: string
  requirementTitle: string
}

export default function TestCasesPage() {
  const [allCases, setAllCases] = useState<FlatTestCase[]>([])
  const [filter, setFilter] = useState<FilterStatus>('all')
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const loadAll = async () => {
      try {
        const { requirements } = await requirementsService.list(0, 50)
        const flat: FlatTestCase[] = []

        for (const req of requirements) {
          const scenarios = await scenariosService.list(req.id)
          for (const scenario of scenarios) {
            const cases = await testCasesService.list(scenario.id)
            for (const tc of cases) {
              flat.push({
                ...tc,
                scenarioTitle: scenario.scenario_title,
                requirementTitle: req.title,
              })
            }
          }
        }
        setAllCases(flat)
      } catch {
        toast.error('Failed to load test cases.')
      } finally {
        setIsLoading(false)
      }
    }
    loadAll()
  }, [])

  const filtered = filter === 'all'
    ? allCases
    : allCases.filter(tc => tc.status === filter)

  const counts = {
    all: allCases.length,
    draft: allCases.filter(tc => tc.status === 'draft').length,
    approved: allCases.filter(tc => tc.status === 'approved').length,
    rejected: allCases.filter(tc => tc.status === 'rejected').length,
  }

  return (
    <div className="p-8 max-w-5xl mx-auto animate-fade-in">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Test Cases</h1>
        <p className="text-gray-500 text-sm mt-1">
          All generated test cases. Expand any to view steps and generate automation scripts.
        </p>
      </div>

      {/* Filter tabs */}
      <div className="flex gap-1 p-1 bg-gray-100 rounded-lg w-fit mb-6">
        {(['all', 'draft', 'approved', 'rejected'] as FilterStatus[]).map(f => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={clsx(
              'px-4 py-1.5 rounded-md text-sm font-medium transition-colors capitalize',
              filter === f
                ? 'bg-white text-gray-900 shadow-sm'
                : 'text-gray-500 hover:text-gray-700'
            )}
          >
            {f} <span className="ml-1 text-xs text-gray-400">({counts[f]})</span>
          </button>
        ))}
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center py-20">
          <Loader2 className="w-8 h-8 text-brand-500 animate-spin" />
        </div>
      ) : filtered.length === 0 ? (
        <div className="card flex flex-col items-center py-16 text-center">
          <ClipboardList className="w-12 h-12 text-gray-300 mb-4" />
          <h3 className="font-semibold text-gray-700 mb-1">
            {filter === 'all' ? 'No test cases yet' : `No ${filter} test cases`}
          </h3>
          <p className="text-gray-400 text-sm mb-4">
            Go to Scenarios to generate test cases from scenarios.
          </p>
          <Link href="/scenarios" className="btn-primary">Go to Scenarios</Link>
        </div>
      ) : (
        <div className="space-y-3">
          {filtered.map(tc => (
            <TestCaseCard key={tc.id} tc={tc} scenarioTitle={tc.scenarioTitle} />
          ))}
        </div>
      )}
    </div>
  )
}
