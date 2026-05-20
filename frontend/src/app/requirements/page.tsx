'use client'

/**
 * src/app/requirements/page.tsx
 * Requirements list with submission form modal
 */

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { Plus, FileText, Loader2, X, AlertCircle } from 'lucide-react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { toast } from 'sonner'
import { requirementsService } from '@/services'
import type { Requirement } from '@/types'
import { getErrorMessage } from '@/lib/api'
import { clsx } from 'clsx'

const schema = z.object({
  title: z.string().min(5, 'Title must be at least 5 characters').max(500),
  description: z.string().min(20, 'Please provide a more detailed description (min 20 chars)').max(5000),
})

type FormData = z.infer<typeof schema>

const STATUS_BADGE: Record<string, string> = {
  submitted: 'badge-gray',
  analyzing: 'badge-yellow',
  analyzed: 'badge-blue',
  scenarios_ready: 'badge-blue',
  test_cases_ready: 'badge-purple',
  approved: 'badge-green',
  automation_generated: 'badge-green',
  completed: 'badge-green',
  failed: 'badge-red',
}

function NewRequirementModal({ onClose, onCreated }: {
  onClose: () => void
  onCreated: (req: Requirement) => void
}) {
  const [isSubmitting, setIsSubmitting] = useState(false)
  const { register, handleSubmit, formState: { errors } } = useForm<FormData>({
    resolver: zodResolver(schema),
  })

  const onSubmit = async (data: FormData) => {
    setIsSubmitting(true)
    try {
      const req = await requirementsService.create(data)
      toast.success('Requirement submitted! AI is analyzing it now.')
      onCreated(req)
      onClose()
    } catch (error) {
      toast.error(getErrorMessage(error))
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-xl w-full max-w-lg animate-slide-up">
        <div className="flex items-center justify-between p-6 border-b border-gray-100">
          <h2 className="font-semibold text-gray-900">Submit New Requirement</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit(onSubmit)} className="p-6 space-y-5">
          <div>
            <label className="label">Requirement Title</label>
            <input
              className="input"
              placeholder="e.g. User Login with email and password"
              {...register('title')}
            />
            {errors.title && <p className="text-red-500 text-xs mt-1">{errors.title.message}</p>}
          </div>

          <div>
            <label className="label">Requirement Description</label>
            <textarea
              className="input min-h-[140px] resize-none"
              placeholder="Describe the feature in detail. Include acceptance criteria, user flows, and any edge cases you know of. The more detail, the better the AI output."
              {...register('description')}
            />
            {errors.description && (
              <p className="text-red-500 text-xs mt-1">{errors.description.message}</p>
            )}
          </div>

          <div className="flex items-center gap-3 pt-2">
            <button type="button" onClick={onClose} className="btn-secondary flex-1">
              Cancel
            </button>
            <button type="submit" disabled={isSubmitting} className="btn-primary flex-1 flex items-center justify-center gap-2">
              {isSubmitting ? (
                <><Loader2 className="w-4 h-4 animate-spin" /> Submitting...</>
              ) : (
                'Submit & Analyze'
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default function RequirementsPage() {
  const [requirements, setRequirements] = useState<Requirement[]>([])
  const [total, setTotal] = useState(0)
  const [isLoading, setIsLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)

  const load = async () => {
    setIsLoading(true)
    try {
      const data = await requirementsService.list()
      setRequirements(data.requirements)
      setTotal(data.total)
    } catch {
      toast.error('Failed to load requirements.')
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  const handleCreated = (req: Requirement) => {
    setRequirements(prev => [req, ...prev])
    setTotal(prev => prev + 1)
  }

  return (
    <div className="p-8 max-w-7xl mx-auto animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Requirements</h1>
          <p className="text-gray-500 text-sm mt-1">{total} total requirements</p>
        </div>
        <button onClick={() => setShowModal(true)} className="btn-primary flex items-center gap-2">
          <Plus className="w-4 h-4" /> New Requirement
        </button>
      </div>

      {/* Content */}
      {isLoading ? (
        <div className="flex items-center justify-center py-20">
          <Loader2 className="w-8 h-8 text-brand-500 animate-spin" />
        </div>
      ) : requirements.length === 0 ? (
        <div className="card flex flex-col items-center justify-center py-16 text-center">
          <FileText className="w-12 h-12 text-gray-300 mb-4" />
          <h3 className="font-semibold text-gray-700 mb-1">No requirements yet</h3>
          <p className="text-gray-400 text-sm mb-4">Submit your first requirement to start generating QA assets</p>
          <button onClick={() => setShowModal(true)} className="btn-primary">
            Submit Requirement
          </button>
        </div>
      ) : (
        <div className="card overflow-hidden">
          <table className="w-full">
            <thead>
              <tr className="bg-gray-50 border-b border-gray-100">
                <th className="text-left text-xs font-semibold text-gray-500 uppercase tracking-wide px-6 py-3">Title</th>
                <th className="text-left text-xs font-semibold text-gray-500 uppercase tracking-wide px-4 py-3">Status</th>
                <th className="text-left text-xs font-semibold text-gray-500 uppercase tracking-wide px-4 py-3">Created</th>
                <th className="px-4 py-3"></th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-50">
              {requirements.map((req) => (
                <tr key={req.id} className="hover:bg-gray-50 transition-colors">
                  <td className="px-6 py-4">
                    <p className="text-sm font-medium text-gray-900">{req.title}</p>
                    <p className="text-xs text-gray-400 mt-0.5 truncate max-w-md">{req.description}</p>
                  </td>
                  <td className="px-4 py-4">
                    <span className={STATUS_BADGE[req.status] ?? 'badge-gray'}>
                      {req.status.replace(/_/g, ' ')}
                    </span>
                  </td>
                  <td className="px-4 py-4 text-xs text-gray-400">
                    {new Date(req.created_at).toLocaleDateString()}
                  </td>
                  <td className="px-4 py-4">
                    <Link
                      href={`/requirements/${req.id}`}
                      className="text-brand-600 text-sm hover:underline font-medium"
                    >
                      View →
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {showModal && (
        <NewRequirementModal
          onClose={() => setShowModal(false)}
          onCreated={handleCreated}
        />
      )}
    </div>
  )
}
