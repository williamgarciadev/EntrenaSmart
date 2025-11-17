import { Router, Route, useLocation } from 'wouter'
import { QueryClientProvider, QueryClient } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { ConfigPage } from './pages/ConfigPage'
import TemplatesPage from './pages/TemplatesPage'
import SchedulesPage from './pages/SchedulesPage'
import StudentsPage from './pages/StudentsPage'
import LoginPage from './pages/LoginPage'
import { WeeklyReminderPage } from './pages/WeeklyReminderPage'
import { ToastProvider } from './components/Toast'
import { Layout } from './components/Layout'
import { AnimatedCard } from './components/AnimatedCard'
import { ProtectedRoute } from './components/ProtectedRoute'
import { AuthProvider } from './hooks/useAuth'
import { Settings, MessageSquare, Clock, Users, Zap, Bell } from 'lucide-react'
import './App.css'

// Crear cliente de query
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 minutos
      gcTime: 1000 * 60 * 10, // 10 minutos (antiguamente cacheTime)
    },
  },
})

function RouterContent() {
  const [location] = useLocation()

  // Ruta de login sin protección
  if (location === '/login') {
    return <LoginPage />
  }

  // Todas las demás rutas requieren autenticación
  return (
    <ProtectedRoute>
      <Layout>
        {(() => {
          switch (location) {
            case '/config':
              return <ConfigPage />
            case '/templates':
              return <TemplatesPage />
            case '/schedules':
              return <SchedulesPage />
            case '/students':
              return <StudentsPage />
            case '/weekly-reminder':
              return <WeeklyReminderPage />
            case '/':
              return <HomePage />
            default:
              return <NotFound />
          }
        })()}
      </Layout>
    </ProtectedRoute>
  )
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <ToastProvider>
          <Router>
            <RouterContent />
          </Router>
        </ToastProvider>
      </AuthProvider>
    </QueryClientProvider>
  )
}

function HomePage() {
  const features = [
    {
      href: '/config',
      label: 'Configuración',
      icon: Settings,
      description: 'Configure los entrenamientos de cada día',
      color: 'from-blue-500 to-blue-600',
    },
    {
      href: '/templates',
      label: 'Plantillas',
      icon: MessageSquare,
      description: 'Crea plantillas de mensajes personalizadas',
      color: 'from-green-500 to-green-600',
    },
    {
      href: '/schedules',
      label: 'Programación',
      icon: Clock,
      description: 'Configura envíos automáticos en horarios',
      color: 'from-purple-500 to-purple-600',
    },
    {
      href: '/students',
      label: 'Estudiantes',
      icon: Users,
      description: 'Administra los estudiantes inscritos',
      color: 'from-orange-500 to-orange-600',
    },
    {
      href: '/weekly-reminder',
      label: 'Recordatorio Semanal',
      icon: Bell,
      description: 'Configura mensajes semanales automáticos',
      color: 'from-pink-500 to-pink-600',
    },
  ]

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <div className="bg-gradient-to-br from-primary to-primary/80 text-white">
        <div className="max-w-6xl mx-auto px-4 py-12 md:py-16">
          <div className="flex items-center gap-3 mb-4">
            <Zap className="w-8 h-8" />
            <h1 className="text-4xl md:text-5xl font-bold">EntrenaSmart</h1>
          </div>
          <p className="text-lg text-primary-foreground/90 max-w-2xl">
            Panel de administración inteligente para gestionar entrenamientos, plantillas de mensajes,
            programación automática y estudiantes. Todo lo que necesitas en un solo lugar.
          </p>
        </div>
      </div>

      {/* Features Grid */}
      <div className="max-w-6xl mx-auto px-4 py-12">
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5, staggerChildren: 0.1 }}
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-6"
        >
          {features.map((feature, index) => {
            const Icon = feature.icon
            return (
              <AnimatedCard
                key={feature.href}
                variant="glass"
                delay={index * 0.1}
                hoverScale={1.05}
              >
                <a
                  href={feature.href}
                  className="group block h-full"
                >
                  <div className="flex flex-col h-full">
                    <motion.div
                      className={`w-12 h-12 rounded-lg bg-gradient-to-br ${feature.color} flex items-center justify-center mb-4 text-white shadow-lg glow-effect`}
                      whileHover={{ scale: 1.1, rotate: 5 }}
                      transition={{ type: 'spring', stiffness: 300, damping: 15 }}
                    >
                      <Icon className="w-6 h-6" />
                    </motion.div>
                    <h3 className="text-lg font-semibold text-foreground mb-2 group-hover:text-primary transition-colors">
                      {feature.label}
                    </h3>
                    <p className="text-sm text-muted-foreground flex-1">
                      {feature.description}
                    </p>
                  </div>
                </a>
              </AnimatedCard>
            )
          })}
        </motion.div>
      </div>

      {/* Stats Section */}
      <div className="py-12 mt-8">
        <div className="max-w-6xl mx-auto px-4">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.3 }}
            className="grid grid-cols-1 md:grid-cols-3 gap-6"
          >
            {[
              { value: '5', label: 'Módulos Principales', color: 'from-blue-500 to-blue-600' },
              { value: '100%', label: 'Funcional', color: 'from-green-500 to-green-600' },
              { value: 'Realtime', label: 'Actualizaciones', color: 'from-purple-500 to-purple-600' },
            ].map((stat, idx) => (
              <motion.div
                key={idx}
                whileHover={{ scale: 1.05 }}
                transition={{ type: 'spring', stiffness: 300, damping: 15 }}
                className="glassmorphism rounded-lg p-8 text-center shadow-lg-soft"
              >
                <motion.p
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  transition={{ delay: 0.4 + idx * 0.1, type: 'spring', stiffness: 200 }}
                  className={`text-4xl font-bold bg-gradient-to-r ${stat.color} bg-clip-text text-transparent`}
                >
                  {stat.value}
                </motion.p>
                <p className="text-muted-foreground mt-3 font-medium">{stat.label}</p>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </div>
    </div>
  )
}

function NotFound() {
  return (
    <motion.div
      className="min-h-screen flex items-center justify-center px-4"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5 }}
    >
      <motion.div
        className="text-center"
        initial={{ scale: 0.9, opacity: 0, y: 20 }}
        animate={{ scale: 1, opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.1 }}
      >
        <motion.div
          className="mb-8 inline-block"
          animate={{ y: [0, -10, 0] }}
          transition={{ duration: 3, repeat: Infinity }}
        >
          <div className="glassmorphism rounded-2xl p-12 shadow-lg-soft">
            <motion.p
              className="text-7xl font-bold bg-gradient-to-r from-red-500 to-pink-600 bg-clip-text text-transparent"
              initial={{ scale: 0, rotate: -180 }}
              animate={{ scale: 1, rotate: 0 }}
              transition={{ duration: 0.8, delay: 0.2, type: 'spring', stiffness: 100 }}
            >
              404
            </motion.p>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.3 }}
        >
          <p className="text-3xl font-bold text-foreground mb-3">Página no encontrada</p>
          <p className="text-lg text-muted-foreground mb-8 max-w-md">
            La página que buscas no existe. Vuelve al inicio para continuar explorando.
          </p>
        </motion.div>

        <motion.a
          href="/"
          className="inline-block bg-gradient-to-r from-blue-500 to-blue-600 text-white px-8 py-3 rounded-lg font-medium shadow-lg-soft group"
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.6, delay: 0.4 }}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          <span className="inline-flex items-center gap-2">
            Volver al inicio
            <motion.span
              animate={{ x: [0, 5, 0] }}
              transition={{ duration: 1.5, repeat: Infinity }}
            >
              →
            </motion.span>
          </span>
        </motion.a>
      </motion.div>
    </motion.div>
  )
}

export default App
