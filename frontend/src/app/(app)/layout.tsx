/**
 * src/app/(app)/layout.tsx
 *
 * Shared layout for all authenticated pages.
 * Wraps children with the Sidebar navigation.
 */

import { Sidebar } from '@/components/layout/Sidebar'

export default function AppLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <main className="flex-1 overflow-auto bg-gray-50">
        {children}
      </main>
    </div>
  )
}
