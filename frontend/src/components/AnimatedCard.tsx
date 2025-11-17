import { motion } from 'framer-motion'
import type { ReactNode } from 'react'

interface AnimatedCardProps {
  children: ReactNode
  className?: string
  variant?: 'default' | 'gradient' | 'glass'
  delay?: number
  hoverScale?: number
}

export function AnimatedCard({
  children,
  className = '',
  variant = 'default',
  delay = 0,
  hoverScale = 1.02,
}: AnimatedCardProps) {
  const variantClasses = {
    default: 'bg-card border border-border shadow-md-soft',
    gradient: 'bg-card border border-border shadow-lg-soft card-gradient',
    glass: 'glassmorphism shadow-lg-soft',
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay }}
      whileHover={{ scale: hoverScale }}
      whileTap={{ scale: 0.98 }}
      className={`${variantClasses[variant]} rounded-lg p-6 ${className}`}
    >
      {children}
    </motion.div>
  )
}
