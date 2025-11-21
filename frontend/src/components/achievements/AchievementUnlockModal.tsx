import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import Confetti from 'react-confetti'
import { useWindowSize } from 'react-use'
import { Trophy, Sparkles } from 'lucide-react'
import { Modal } from '@/components/ui/Modal'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'

interface Achievement {
  achievement_id: number
  name: string
  description: string
  icon: string
  xp_reward: number
}

interface AchievementUnlockModalProps {
  open: boolean
  onClose: () => void
  achievements: Achievement[]
}

// Counter animation hook
function useCountUp(end: number, duration: number = 1000) {
  const [count, setCount] = useState(0)

  useEffect(() => {
    if (end === 0) return

    let startTime: number
    let animationFrame: number

    const animate = (timestamp: number) => {
      if (!startTime) startTime = timestamp
      const progress = timestamp - startTime
      const percentage = Math.min(progress / duration, 1)

      // Easing function for smooth animation
      const easeOutQuad = 1 - (1 - percentage) * (1 - percentage)
      setCount(Math.floor(end * easeOutQuad))

      if (percentage < 1) {
        animationFrame = requestAnimationFrame(animate)
      }
    }

    animationFrame = requestAnimationFrame(animate)
    return () => cancelAnimationFrame(animationFrame)
  }, [end, duration])

  return count
}

export function AchievementUnlockModal({
  open,
  onClose,
  achievements,
}: AchievementUnlockModalProps) {
  const { width, height } = useWindowSize()

  // Debug logging
  useEffect(() => {
    console.log('🏆 AchievementUnlockModal props changed:')
    console.log('  - open:', open)
    console.log('  - achievements:', achievements)
    console.log('  - achievements.length:', achievements?.length || 0)
  }, [open, achievements])
  const [showConfetti, setShowConfetti] = useState(false)

  // Calculate total XP
  const totalXP = achievements.reduce((sum, a) => sum + a.xp_reward, 0)
  const animatedXP = useCountUp(totalXP, 1500)

  // Show confetti when modal opens
  useEffect(() => {
    if (open) {
      setShowConfetti(true)
      // Stop confetti after 4 seconds
      const timer = setTimeout(() => setShowConfetti(false), 4000)
      return () => clearTimeout(timer)
    }
  }, [open])

  if (achievements.length === 0) return null

  return (
    <>
      {/* Confetti */}
      <AnimatePresence>
        {showConfetti && (
          <Confetti
            width={width}
            height={height}
            recycle={false}
            numberOfPieces={500}
            gravity={0.3}
            style={{ position: 'fixed', top: 0, left: 0, zIndex: 60 }}
          />
        )}
      </AnimatePresence>

      {/* Modal */}
      <Modal
        open={open}
        onClose={onClose}
        closeOnBackdrop={false}
        showClose={false}
        className="max-w-xl"
      >
        <div className="p-8">
          {/* Header Icon */}
          <motion.div
            initial={{ scale: 0, rotate: -180 }}
            animate={{ scale: 1, rotate: 0 }}
            transition={{
              type: 'spring',
              stiffness: 260,
              damping: 20,
              delay: 0.1,
            }}
            className="flex justify-center mb-6"
          >
            <div className="relative">
              <div className="w-20 h-20 bg-gradient-to-br from-accent-gold-400 to-accent-gold-600 rounded-full flex items-center justify-center shadow-lg">
                <Trophy className="h-10 w-10 text-white" />
              </div>
              {/* Sparkle decorations */}
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ delay: 0.3 }}
                className="absolute -top-2 -right-2"
              >
                <Sparkles className="h-6 w-6 text-accent-gold-400" />
              </motion.div>
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ delay: 0.4 }}
                className="absolute -bottom-1 -left-2"
              >
                <Sparkles className="h-5 w-5 text-accent-gold-500" />
              </motion.div>
            </div>
          </motion.div>

          {/* Title */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="text-center mb-6"
          >
            <h2 className="text-3xl font-bold text-neutral-900 dark:text-slate-100 mb-2">
              {achievements.length === 1 ? 'Achievement Unlocked!' : 'Achievements Unlocked!'}
            </h2>
            <p className="text-neutral-600 dark:text-slate-400">
              Congratulations! You've earned new achievements!
            </p>
          </motion.div>

          {/* Achievements List */}
          <div className="space-y-4 mb-6">
            {achievements.map((achievement, index) => (
              <motion.div
                key={achievement.achievement_id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.3 + index * 0.1 }}
                className="bg-gradient-to-r from-primary-50 to-accent-purple-50 dark:from-primary-900/20 dark:to-accent-purple-900/20 border-2 border-primary-200 dark:border-primary-700 rounded-lg p-4"
              >
                <div className="flex items-start gap-4">
                  {/* Achievement Icon */}
                  <div className="flex-shrink-0">
                    <div className="w-16 h-16 bg-white dark:bg-slate-700 rounded-lg flex items-center justify-center text-3xl shadow-sm">
                      {achievement.icon}
                    </div>
                  </div>

                  {/* Achievement Info */}
                  <div className="flex-1 min-w-0">
                    <h3 className="font-bold text-lg text-neutral-900 dark:text-slate-100 mb-1">
                      {achievement.name}
                    </h3>
                    <p className="text-sm text-neutral-600 dark:text-slate-400 mb-2">
                      {achievement.description}
                    </p>
                    <Badge variant="info">
                      +{achievement.xp_reward} XP
                    </Badge>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>

          {/* Total XP Earned */}
          {achievements.length > 1 && (
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.5 + achievements.length * 0.1 }}
              className="text-center mb-6 p-4 bg-accent-purple-100 dark:bg-accent-purple-900/30 rounded-lg"
            >
              <p className="text-sm text-neutral-600 dark:text-slate-400 mb-1">
                Total XP Earned
              </p>
              <p className="text-4xl font-bold text-accent-purple-600 dark:text-accent-purple-400">
                +{animatedXP} XP
              </p>
            </motion.div>
          )}

          {/* Close Button */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.7 + achievements.length * 0.1 }}
          >
            <Button
              onClick={onClose}
              className="w-full"
              size="lg"
            >
              Awesome!
            </Button>
          </motion.div>
        </div>
      </Modal>
    </>
  )
}
