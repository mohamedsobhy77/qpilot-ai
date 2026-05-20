'use client'

/**
 * src/app/auth/login/page.tsx
 * Login page — email/password form with JWT auth
 */

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { toast } from 'sonner'
import { Loader2, Bot } from 'lucide-react'
import { authService } from '@/services'
import { useAuthStore } from '@/store/auth'
import { getErrorMessage } from '@/lib/api'

const schema = z.object({
  email: z.string().email('Please enter a valid email address'),
  password: z.string().min(6, 'Password must be at least 6 characters'),
})

type LoginForm = z.infer<typeof schema>

export default function LoginPage() {
  const router = useRouter()
  const { setAuth } = useAuthStore()
  const [isLoading, setIsLoading] = useState(false)

  const { register, handleSubmit, formState: { errors } } = useForm<LoginForm>({
    resolver: zodResolver(schema),
  })

  const onSubmit = async (data: LoginForm) => {
    setIsLoading(true)
    try {
      const response = await authService.login(data)
      setAuth(response.access_token, response.user)
      toast.success('Welcome back!')
      router.push('/dashboard')
    } catch (error) {
      toast.error(getErrorMessage(error))
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-brand-50 via-white to-indigo-50 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-brand-600 rounded-2xl shadow-lg mb-4">
            <Bot className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-2xl font-bold text-gray-900">QPilot AI</h1>
          <p className="text-gray-500 text-sm mt-1">AI-Powered QA Automation Platform</p>
        </div>

        {/* Card */}
        <div className="card p-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-6">Sign in to your account</h2>

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
            {/* Email */}
            <div>
              <label className="label">Email address</label>
              <input
                type="email"
                className="input"
                placeholder="qa@company.com"
                {...register('email')}
              />
              {errors.email && (
                <p className="text-red-500 text-xs mt-1">{errors.email.message}</p>
              )}
            </div>

            {/* Password */}
            <div>
              <label className="label">Password</label>
              <input
                type="password"
                className="input"
                placeholder="••••••••"
                {...register('password')}
              />
              {errors.password && (
                <p className="text-red-500 text-xs mt-1">{errors.password.message}</p>
              )}
            </div>

            {/* Submit */}
            <button
              type="submit"
              disabled={isLoading}
              className="btn-primary w-full flex items-center justify-center gap-2"
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Signing in...
                </>
              ) : (
                'Sign in'
              )}
            </button>
          </form>

          {/* Demo note */}
          <div className="mt-6 p-3 bg-blue-50 rounded-lg">
            <p className="text-xs text-blue-700 font-medium">Demo credentials</p>
            <p className="text-xs text-blue-600 mt-0.5">
              Email: <code>admin@qpilot.ai</code> / Password: <code>qpilot123</code>
            </p>
          </div>
        </div>

        <p className="text-center text-xs text-gray-400 mt-6">
          © {new Date().getFullYear()} QPilot AI. All rights reserved.
        </p>
      </div>
    </div>
  )
}
