import type { Metadata } from 'next'
import { Toaster } from 'sonner'
import './globals.css'

export const metadata: Metadata = {
  title: 'QPilot AI — QA Automation Platform',
  description: 'AI-powered QA automation: transform requirements into test cases, Playwright scripts, and Jira tickets automatically.',
  icons: { icon: '/favicon.ico' },
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body>
        {children}
        <Toaster position="top-right" richColors closeButton />
      </body>
    </html>
  )
}
