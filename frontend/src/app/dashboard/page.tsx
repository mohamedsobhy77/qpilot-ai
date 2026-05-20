'use client'

/**
 * src/app/dashboard/page.tsx
 * Main dashboard — stats overview and recent requirements
 */

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { FileText, FlaskConical, ClipboardList, Code2, Clock, CheckCircle, AlertCircle, Loader2 } from 'lucide-react'
import { dashboardService } from '@/services'
import type { DashboardStats, Requirement } from '@/types'
import { clsx } from 'clsx'

const STATUS_BADGE: Record<string, string> = {
  submitted:           'badge-gray',
  analyzing:           'badge-yellow',
  analyzed:            'badge-blue',
  scenarios_ready:     'badge-blue',
  test_cases_ready:    'badge-purple',
  approved:            'badge-green',
  automation_generated:'badge-green',
  completed:           'badge-green',
  failed:              'badge-red',
}

function StatCard({ icon: Icon, label, value, color }: {
  icon: React.ElementType
  label: string
  value: number
  color: string
}) {
  return (
    <div className="card p-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-gray-500 font-medium">{label}</p>
          <p className="text-3xl font-bold text-gray-900 mt-1">{value}</p>
        </div>
        <div className={clsx('w-12 h-12 rounded-xl flex items-center justify-center', color)}>
          <Icon className="w-6 h-6" />
        </div>
      </div>
    </div>
  )
}

function RequirementRow({ req }: { req: Requirement }) {
  return (
    <Link
      href={`/requirements/${req.id}`}
      className="flex items-center justify-between py-3 px-4 hover:bg-gray-50 rounded-lg transition-colors group"
    >
      <div className="min-w-0 flex-1">
        <p className="text-sm font-medium text-gray-900 truncate group-hover:text-brand-600 transition-colors">
          {req.title}
        </p>
        <p className="text-xs text-gray-400 mt-0.5">
          {new Date(req.created_at).toLocaleDateString('en-US', {
            month: 'short', day: 'numeric', year: 'numeric'
          })}
        </p>
      </div>
      <span className={STATUS_BADGE[req.status] ?? 'badge-gray'}>
        {req.status.replace(/_/g, ' ')}
      </span>
    </Link>
  )
}

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    dashboardService.getStats()
      .then(setStats)
      .catch(() => setError('Failed to load dashboard data.'))
      .finally(() => setIsLoading(false))
  }, [])

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader2 className="w-8 h-8 text-brand-500 animate-spin" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="p-8">
        <div className="flex items-center gap-2 text-red-600">
          <AlertCircle className="w-5 h-5" /> {error}
        </div>
      </div>
    )
  }

  return (
    <div className="p-8 max-w-7xl mx-auto animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-500 text-sm mt-1">QPilot AI QA automation overview</p>
        </div>
        <Link href="/requirements/new" className="btn-primary">
          + New Requirement
        </Link>
      </div>

      {/* Stats grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-6 mb-8">
        <StatCard
          icon={FileText}
          label="Total Requirements"
          value={stats?.total_requirements ?? 0}
          color="bg-blue-100 text-blue-600"
        />
        <StatCard
          icon={FlaskConical}
          label="Scenarios Generated"
          value={stats?.total_scenarios ?? 0}
          color="bg-purple-100 text-purple-600"
        />
        <StatCard
          icon={ClipboardList}
          label="Test Cases Generated"
          value={stats?.total_test_cases ?? 0}
          color="bg-green-100 text-green-600"
        />
        <StatCard
          icon={Code2}
          label="Scripts Generated"
          value={stats?.total_scripts_generated ?? 0}
          color="bg-orange-100 text-orange-600"
        />
      </div>

      {/* Bottom row */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        {/* Recent requirements */}
        <div className="card xl:col-span-2">
          <div className="flex items-center justify-between p-6 border-b border-gray-100">
            <h2 className="font-semibold text-gray-900">Recent Requirements</h2>
            <Link href="/requirements" className="text-brand-600 text-sm hover:underline">
              View all
            </Link>
          </div>
          <div className="p-2">
            {stats?.recent_requirements?.length ? (
              stats.recent_requirements.map((req) => (
                <RequirementRow key={req.id} req={req} />
              ))
            ) : (
              <div className="text-center py-8 text-gray-400">
                <FileText className="w-8 h-8 mx-auto mb-2 opacity-40" />
                <p className="text-sm">No requirements yet</p>
                <Link href="/requirements/new" className="text-brand-600 text-sm hover:underline mt-1 block">
                  Submit your first requirement →
                </Link>
              </div>
            )}
          </div>
        </div>

        {/* Pending approvals */}
        <div className="card">
          <div className="p-6 border-b border-gray-100">
            <h2 className="font-semibold text-gray-900">Pending Approvals</h2>
          </div>
          <div className="p-6">
            {(stats?.pending_approvals ?? 0) > 0 ? (
              <div className="flex items-center gap-3 p-4 bg-yellow-50 rounded-lg">
                <Clock className="w-5 h-5 text-yellow-600 flex-shrink-0" />
                <div>
                  <p className="text-sm font-medium text-yellow-800">
                    {stats?.pending_approvals} awaiting review
                  </p>
                  <Link href="/requirements?status=test_cases_ready" className="text-yellow-600 text-xs hover:underline">
                    Review now →
                  </Link>
                </div>
              </div>
            ) : (
              <div className="flex items-center gap-3 p-4 bg-green-50 rounded-lg">
                <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0" />
                <p className="text-sm text-green-700 font-medium">All caught up!</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
