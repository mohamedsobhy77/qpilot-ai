'use client'

/**
 * src/app/workflows/page.tsx
 *
 * Workflow execution history — shows running, completed, and failed runs.
 * Auto-polls every 5s while any workflow is in "running" state.
 */

import { useEffect, useRef, useState } from 'react'
import {
  Workflow, CheckCircle, XCircle, Loader2,
  Clock, RefreshCw, Activity,
} from 'lucide-react'
import { toast } from 'sonner'
import { api } from '@/lib/api'
import type { WorkflowExecution } from '@/types'
import { clsx } from 'clsx'

async function fetchWorkflows(): Promise<WorkflowExecution[]> {
  const res = await api.get<{
    success: boolean
    data: { executions: WorkflowExecution[]; total: number }
  }>('/workflows')
  return res.data.data?.executions ?? []
}

function StatusIcon({ status }: { status: string }) {
  if (status === 'running')
    return <Loader2 className="w-4 h-4 text-blue-500 animate-spin" />
  if (status === 'success')
    return <CheckCircle className="w-4 h-4 text-green-500" />
  if (status === 'failed')
    return <XCircle className="w-4 h-4 text-red-500" />
  return <Clock className="w-4 h-4 text-gray-400" />
}

function StatusBadge({ status }: { status: string }) {
  const cls = {
    running: 'badge-blue',
    success: 'badge-green',
    failed:  'badge-red',
  }[status] ?? 'badge-gray'
  return <span className={cls}>{status}</span>
}

function duration(started: string, completed?: string | null): string {
  const start = new Date(started).getTime()
  const end = completed ? new Date(completed).getTime() : Date.now()
  const secs = Math.round((end - start) / 1000)
  if (secs < 60) return `${secs}s`
  return `${Math.floor(secs / 60)}m ${secs % 60}s`
}

function WorkflowRow({ exec }: { exec: WorkflowExecution }) {
  const [showLogs, setShowLogs] = useState(false)
  return (
    <div className="card mb-3 overflow-hidden">
      <div
        className="flex items-center gap-4 p-5 cursor-pointer hover:bg-gray-50 transition-colors"
        onClick={() => exec.logs && setShowLogs(!showLogs)}
      >
        <StatusIcon status={exec.execution_status} />
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <p className="font-medium text-gray-900 text-sm">{exec.workflow_name}</p>
            <StatusBadge status={exec.execution_status} />
          </div>
          <p className="text-xs text-gray-400 mt-0.5">
            Started {new Date(exec.started_at).toLocaleString()} ·{' '}
            Duration: {duration(exec.started_at, exec.completed_at)}
          </p>
          {exec.error_message && (
            <p className="text-xs text-red-600 mt-1 font-mono">{exec.error_message}</p>
          )}
        </div>
        <div className="text-xs text-gray-400 font-mono hidden md:block">
          {exec.id.slice(0, 8)}…
        </div>
        {exec.logs && (
          <span className="text-xs text-brand-600 hover:underline flex-shrink-0">
            {showLogs ? 'Hide logs' : 'View logs'}
          </span>
        )}
      </div>

      {showLogs && exec.logs && (
        <div className="border-t border-gray-100 bg-gray-900 p-4">
          <pre className="text-xs text-gray-300 whitespace-pre-wrap font-mono leading-relaxed">
            {exec.logs}
          </pre>
        </div>
      )}
    </div>
  )
}

export default function WorkflowsPage() {
  const [executions, setExecutions] = useState<WorkflowExecution[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [lastRefresh, setLastRefresh] = useState(new Date())
  const pollRef = useRef<NodeJS.Timeout | null>(null)

  const load = async (silent = false) => {
    if (!silent) setIsLoading(true)
    try {
      const data = await fetchWorkflows()
      setExecutions(data)
      setLastRefresh(new Date())
    } catch {
      if (!silent) toast.error('Failed to load workflow executions.')
    } finally {
      if (!silent) setIsLoading(false)
    }
  }

  // Auto-poll while any workflow is running
  useEffect(() => {
    load()
  }, [])

  useEffect(() => {
    const hasRunning = executions.some(e => e.execution_status === 'running')
    if (hasRunning) {
      pollRef.current = setInterval(() => load(true), 5000)
    } else {
      if (pollRef.current) clearInterval(pollRef.current)
    }
    return () => { if (pollRef.current) clearInterval(pollRef.current) }
  }, [executions])

  const stats = {
    total: executions.length,
    running: executions.filter(e => e.execution_status === 'running').length,
    success: executions.filter(e => e.execution_status === 'success').length,
    failed: executions.filter(e => e.execution_status === 'failed').length,
  }

  return (
    <div className="p-8 max-w-5xl mx-auto animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Workflows</h1>
          <p className="text-gray-500 text-sm mt-1">
            n8n pipeline execution history. Auto-refreshes while jobs are running.
          </p>
        </div>
        <button
          onClick={() => load()}
          disabled={isLoading}
          className="btn-secondary flex items-center gap-2"
        >
          <RefreshCw className={clsx('w-4 h-4', isLoading && 'animate-spin')} />
          Refresh
        </button>
      </div>

      {/* Stats bar */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        {[
          { label: 'Total runs', value: stats.total,   color: 'text-gray-700' },
          { label: 'Running',    value: stats.running,  color: 'text-blue-600' },
          { label: 'Succeeded',  value: stats.success,  color: 'text-green-600' },
          { label: 'Failed',     value: stats.failed,   color: 'text-red-600' },
        ].map(s => (
          <div key={s.label} className="card p-4 text-center">
            <p className={clsx('text-2xl font-bold', s.color)}>{s.value}</p>
            <p className="text-xs text-gray-500 mt-1">{s.label}</p>
          </div>
        ))}
      </div>

      {/* Last refresh note */}
      {stats.running > 0 && (
        <div className="flex items-center gap-2 text-sm text-blue-600 bg-blue-50 rounded-lg px-4 py-3 mb-6">
          <Activity className="w-4 h-4 animate-pulse" />
          <span>{stats.running} workflow{stats.running > 1 ? 's' : ''} running — auto-refreshing every 5s</span>
          <span className="ml-auto text-xs text-blue-400">
            Last: {lastRefresh.toLocaleTimeString()}
          </span>
        </div>
      )}

      {/* List */}
      {isLoading ? (
        <div className="flex items-center justify-center py-20">
          <Loader2 className="w-8 h-8 text-brand-500 animate-spin" />
        </div>
      ) : executions.length === 0 ? (
        <div className="card flex flex-col items-center py-16 text-center">
          <Workflow className="w-12 h-12 text-gray-300 mb-4" />
          <h3 className="font-semibold text-gray-700 mb-1">No workflow executions yet</h3>
          <p className="text-gray-400 text-sm">
            Submit a requirement to trigger the automation pipeline.
          </p>
        </div>
      ) : (
        <div>
          {executions.map(exec => (
            <WorkflowRow key={exec.id} exec={exec} />
          ))}
        </div>
      )}
    </div>
  )
}
