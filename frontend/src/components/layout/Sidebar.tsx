'use client'

/**
 * src/components/layout/Sidebar.tsx
 * App sidebar with navigation links and user info
 */

import Link from 'next/link'
import { usePathname, useRouter } from 'next/navigation'
import {
  Bot, LayoutDashboard, FileText, FlaskConical,
  ClipboardList, Workflow, ScrollText, LogOut
} from 'lucide-react'
import { useAuthStore } from '@/store/auth'
import { clsx } from 'clsx'

const nav = [
  { label: 'Dashboard',    href: '/dashboard',   icon: LayoutDashboard },
  { label: 'Requirements', href: '/requirements', icon: FileText },
  { label: 'Scenarios',    href: '/scenarios',    icon: FlaskConical },
  { label: 'Test Cases',   href: '/test-cases',   icon: ClipboardList },
  { label: 'Workflows',    href: '/workflows',    icon: Workflow },
  { label: 'Logs',         href: '/logs',         icon: ScrollText },
]

export function Sidebar() {
  const pathname = usePathname()
  const router = useRouter()
  const { user, clearAuth } = useAuthStore()

  const handleLogout = () => {
    clearAuth()
    router.push('/auth/login')
  }

  return (
    <aside className="flex flex-col w-64 bg-gray-900 min-h-screen">
      {/* Logo */}
      <div className="flex items-center gap-3 px-6 py-5 border-b border-gray-800">
        <div className="w-8 h-8 bg-brand-500 rounded-lg flex items-center justify-center flex-shrink-0">
          <Bot className="w-4 h-4 text-white" />
        </div>
        <div>
          <p className="text-white font-semibold text-sm leading-none">QPilot AI</p>
          <p className="text-gray-500 text-xs mt-0.5">QA Automation</p>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 py-4 space-y-1">
        {nav.map(({ label, href, icon: Icon }) => {
          const active = pathname === href || pathname.startsWith(href + '/')
          return (
            <Link
              key={href}
              href={href}
              className={clsx(
                'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors',
                active
                  ? 'bg-brand-600 text-white'
                  : 'text-gray-400 hover:text-white hover:bg-gray-800'
              )}
            >
              <Icon className="w-4 h-4 flex-shrink-0" />
              {label}
            </Link>
          )
        })}
      </nav>

      {/* User */}
      <div className="px-3 pb-4 border-t border-gray-800 pt-4">
        <div className="flex items-center gap-3 px-3 py-2 mb-2">
          <div className="w-8 h-8 rounded-full bg-brand-600 flex items-center justify-center text-white text-xs font-bold flex-shrink-0">
            {user?.full_name?.charAt(0)?.toUpperCase() ?? 'U'}
          </div>
          <div className="min-w-0">
            <p className="text-white text-sm font-medium truncate">{user?.full_name ?? 'User'}</p>
            <p className="text-gray-500 text-xs truncate">{user?.role}</p>
          </div>
        </div>
        <button
          onClick={handleLogout}
          className="flex items-center gap-3 w-full px-3 py-2 rounded-lg text-sm text-gray-400 hover:text-white hover:bg-gray-800 transition-colors"
        >
          <LogOut className="w-4 h-4" />
          Sign out
        </button>
      </div>
    </aside>
  )
}
