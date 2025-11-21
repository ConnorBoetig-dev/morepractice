import { useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { X } from 'lucide-react'
import { cn } from '@/lib/utils'

interface ModalProps {
  open: boolean
  onClose: () => void
  children: React.ReactNode
  className?: string
  showClose?: boolean
  closeOnBackdrop?: boolean
  closeOnEsc?: boolean
}

export function Modal({
  open,
  onClose,
  children,
  className,
  showClose = true,
  closeOnBackdrop = true,
  closeOnEsc = true,
}: ModalProps) {
  // Handle ESC key
  useEffect(() => {
    if (!open || !closeOnEsc) return

    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose()
      }
    }

    document.addEventListener('keydown', handleEscape)
    return () => document.removeEventListener('keydown', handleEscape)
  }, [open, closeOnEsc, onClose])

  // Prevent body scroll when modal is open
  useEffect(() => {
    if (open) {
      document.body.style.overflow = 'hidden'
    } else {
      document.body.style.overflow = 'unset'
    }
    return () => {
      document.body.style.overflow = 'unset'
    }
  }, [open])

  return (
    <AnimatePresence>
      {open && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
            onClick={closeOnBackdrop ? onClose : undefined}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50"
            aria-hidden="true"
          />

          {/* Modal Content */}
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 pointer-events-none">
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              transition={{ duration: 0.2 }}
              onClick={(e) => e.stopPropagation()}
              className={cn(
                'relative bg-white dark:bg-slate-800 rounded-xl shadow-2xl',
                'max-w-lg w-full max-h-[90vh] overflow-y-auto',
                'pointer-events-auto',
                className
              )}
              role="dialog"
              aria-modal="true"
            >
              {/* Close Button */}
              {showClose && (
                <button
                  onClick={onClose}
                  className="absolute top-4 right-4 p-2 rounded-lg text-neutral-400 hover:text-neutral-600 dark:text-slate-400 dark:hover:text-slate-200 hover:bg-neutral-100 dark:hover:bg-slate-700 transition-colors"
                  aria-label="Close modal"
                >
                  <X className="h-5 w-5" />
                </button>
              )}

              {/* Content */}
              {children}
            </motion.div>
          </div>
        </>
      )}
    </AnimatePresence>
  )
}
