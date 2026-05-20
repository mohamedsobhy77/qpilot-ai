'use client'

/**
 * src/app/logs/page.tsx
 *
 * Platform-wide activity log: requirements submitted, scenarios generated,
 * approvals, script pushes, Jira tickets, Slack notifications.
 */

import { useEffect, useState } from 'react'
import {
  ScrollText, FileText, FlaskConical, ClipboardList,
  CheckCircle, XCircle, Code2, Bell, Loader2,
} from 'lucide-react'
import { requirementsService } from '@/services'
import type { Requirement } from '@/types'
import { toast } from 'sonner'
import { clsx } from 'clsx'

// Build a flat activity list from requirements data
interface ActivityEntry {
  id: string
  icon: React.ElementType
  iconColor: string
  title: string
  detail: string
  time: string
  badge?: string
  badgeClass?: string
}

function buildActivity(requirements: Requirement[]): ActivityEntry[] {
  const entries: ActivityEntry[] = []

  for (const req of requirements) {
    entries.push({
      id: `req-${req.id}`,
      icon: FileText,
      iconColor: 'text-blue-500',
      title: 'Requirement submitted',
      detail: req.title,
      time: req.created_at,
      badge: req.status.replace(/_/g, ' '),
      badgeClass: {
        submitted: 'badge-gray',
        analyzing: 'badge-yellow',
        analyzed: 'badge-blue',
        scenarios_ready: 'badge-blue',
        test_cases_ready: 'badge-purple',
        approved: 'badge-green',
        automation_generated: 'badge-green',
        completed: 'badge-green',
        failed: 'badge-red',
      }[req.status] ?? 'badge-gray',
    })

    if (['scenarios_ready', 'test_cases_ready', 'approved', 'automation_generated', 'completed'].includes(req.status)) {
      entries.push({
        id: `scenarios-${req.id}`,
        icon: FlaskConical,
        iconColor: 'text-purple-500',
        title: 'Scenarios generated',
        detail: req.title,
        time: req.updated_at,
      })
    }

    if (['test_cases_ready', 'approved', 'automation_generated', 'completed'].includes(req.status)) {
      entries.push({
        id: `testcases-${req.id}`,
        icon: ClipboardList,
        iconColor: 'text-indigo-500',
        title: 'Test cases generated',
        detail: req.title,
        time: req.updated_at,
      })
    }

    if (req.status === 'approved') {
      entries.push({
        id: `approval-${req.id}`,
        icon: CheckCircle,
        iconColor: 'text-green-500',
        title: 'QA approved',
        detail: req.title,
        time: req.updated_at,
        badge: 'approved',
        badgeClass: 'badge-green',
      })
    }

    if (['automation_generated', 'completed'].includes(req.status)) {
      entries.push({
        id: `script-${req.id}`,
        icon: Code2,
        iconColor: 'text-orange-500',
        title: 'Playwright scripts generated & pushed to GitHub',
        detail: req.title,
        time: req.updated_at,
      })
    }

    if (req.status === 'failed') {
      entries.push({
        id: `failed-${req.id}`,
        icon: XCircle,
        iconColor: 'text-red-500',
        title: 'Pipeline failed',
        detail: req.title,
        time: req.updated_at,
        badge: 'failed',
        badgeClass: 'badge-red',
      })
    }
  }

  // Sort newest first
  return entries.sort((a, b) => new Date(b.time).getTime() - new Date(a.time).getTime())
}

function relativeTime(iso: string): string {
  const diff = Date.now() - new Date(iso).getTime()
  const mins = Math.floor(diff / 60000)
  if (mins < 1) return 'just now'
  if (mins < 60) return `${mins}m ago`
  const hrs = Math.floor(mins / 60)
  if (hrs < 24) return `${hrs}h ago`
  return `${Math.floor(hrs / 24)}d ago`
}

export default function LogsPage() {
  const [entries, setEntries] = useState<ActivityEntry[]>([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    requirementsService.list(0, 100)
      .then(data => setEntries(buildActivity(data.requirements)))
      .catch(() => toast.error('Failed to load activity log.'))
      .finally(() => setIsLoading(false))
  }, [])

  return (
    <div className="p-8 max-w-4xl mx-auto animate-fade-in">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Activity Log</h1>
        <p className="text-gray-500 text-sm mt-1">
          Complete history of all platform events — submissions, generations, approvals, and pushes.
        </p>
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center py-20">
          <Loader2 className="w-8 h-8 text-brand-500 animate-spin" />
        </div>
      ) : entries.length === 0 ? (
        <div className="card flex flex-col items-center py-16 text-center">
          <ScrollText className="w-12 h-12 text-gray-300 mb-4" />
          <h3 className="font-semibold text-gray-700 mb-1">No activity yet</h3>
          <p className="text-gray-400 text-sm">
            Activity will appear here as you use the platform.
          </p>
        </div>
      ) : (
        <div className="card overflow-hidden">
          <div className="divide-y divide-gray-50">
            {entries.map((entry, i) => {
              const Icon = entry.icon
              return (
                <div
                  key={entry.id}
                  className={clsx(
                    'flex items-start gap-4 px-6 py-4',
                    'hover:bg-gray-50 transition-colors'
                  )}
                >
                  {/* Icon col */}
                  <div className={clsx(
                    'w-8 h-8 rounded-full bg-gray-100 flex items-center justify-center flex-shrink-0 mt-0.5',
                  )}>
                    <Icon className={clsx('w-4 h-4', entry.iconColor)} />
                  </div>

                  {/* Content */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 flex-wrap">
                      <p className="text-sm font-medium text-gray-900">{entry.title}</p>
                      {entry.badge && (
                        <span className={entry.badgeClass}>{entry.badge}</span>
                      )}
                    </div>
                    <p className="text-xs text-gray-500 mt-0.5 truncate">{entry.detail}</p>
                  </div>

                  {/* Time */}
                  <p className="text-xs text-gray-400 flex-shrink-0 mt-0.5">
                    {relativeTime(entry.time)}
                  </p>
                </div>
              )
            })}
          </div>

          {/* Footer */}
          <div className="px-6 py-3 bg-gray-50 border-t border-gray-100">
            <p className="text-xs text-gray-400 text-center">
              {entries.length} events · Showing all activity
            </p>
          </div>
        </div>
      )}
    </div>
  )
}
