import { Menu, X, LogOut, Zap } from 'lucide-react'
import { useState } from 'react'
import { motion } from 'framer-motion'

interface NavbarProps {
  onMenuToggle: () => void
  isMenuOpen: boolean
}

export function Navbar({ onMenuToggle, isMenuOpen }: NavbarProps) {
  return (
    <motion.nav
      className="sticky top-0 z-40 glassmorphism border-b border-border/50 shadow-lg-soft"
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <div className="px-4 py-3 flex items-center justify-between">
        {/* Logo y título */}
        <div className="flex items-center gap-3">
          <motion.button
            onClick={onMenuToggle}
            className="p-2 hover:bg-accent/10 rounded-lg transition-colors-smooth md:hidden"
            aria-label="Toggle menu"
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.95 }}
          >
            {isMenuOpen ? (
              <motion.div
                initial={{ rotate: 0 }}
                animate={{ rotate: 90 }}
                transition={{ duration: 0.3 }}
              >
                <X className="w-5 h-5 text-foreground" />
              </motion.div>
            ) : (
              <Menu className="w-5 h-5 text-foreground" />
            )}
          </motion.button>

          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
            className="flex items-center gap-2"
          >
            <div className="p-2 bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg shadow-md-soft">
              <Zap className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-foreground">EntrenaSmart</h1>
              <p className="text-xs text-muted-foreground">Backoffice</p>
            </div>
          </motion.div>
        </div>

        {/* User menu */}
        <motion.div
          className="flex items-center gap-4"
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
        >
          <div className="text-right">
            <p className="text-sm font-medium text-foreground">Admin</p>
            <p className="text-xs text-muted-foreground">Entrenador</p>
          </div>
          <motion.button
            className="p-2 hover:bg-red-50 rounded-lg transition-colors-smooth text-destructive hover-lift"
            whileHover={{ scale: 1.1, rotate: 10 }}
            whileTap={{ scale: 0.9 }}
          >
            <LogOut className="w-5 h-5" />
          </motion.button>
        </motion.div>
      </div>
    </motion.nav>
  )
}
