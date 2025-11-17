import type { ReactNode } from 'react'

interface BadgeProps {
  variant?: 'default' | 'success' | 'danger' | 'warning' | 'info' | 'secondary'
  size?: 'sm' | 'md'
  children: ReactNode
  className?: string
}

export function Badge({
  variant = 'default',
  size = 'md',
  children,
  className = '',
}: BadgeProps) {
  const variants = {
    default: 'bg-gray-100 text-gray-800',
    success: 'bg-green-100 text-green-800',
    danger: 'bg-red-100 text-red-800',
    warning: 'bg-yellow-100 text-yellow-800',
    info: 'bg-blue-100 text-blue-800',
    secondary: 'bg-purple-100 text-purple-800',
  }

  const sizes = {
    sm: 'px-2 py-0.5 text-xs font-medium',
    md: 'px-3 py-1 text-sm font-medium',
  }

  return (
    <span
      className={`inline-block rounded-full ${variants[variant]} ${sizes[size]} ${className}`}
    >
      {children}
    </span>
  )
}
