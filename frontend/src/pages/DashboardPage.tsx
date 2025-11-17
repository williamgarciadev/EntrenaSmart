/**
 * DashboardPage - Panel principal del entrenador
 *
 * Muestra información contextual y métricas clave:
 * - Resumen de estudiantes (total, activos, nuevos)
 * - Entrenamientos de hoy
 * - Próximos entrenamientos
 * - Acciones rápidas
 */

import { useState, useEffect } from 'react'
import { Users, Calendar, TrendingUp, Clock, Plus, Settings } from 'lucide-react'
import { useStudents } from '@/hooks/useStudents'
import { useWeeklyConfig } from '@/hooks/useTrainingConfig'
import { Button } from '@/components/ui/Button'
import { Skeleton } from '@/components/ui/Skeleton'
import { Link } from 'react-router-dom'

export default function DashboardPage() {
  const { data: studentsData, isLoading: loadingStudents } = useStudents()
  const { data: weeklyConfig, isLoading: loadingConfig } = useWeeklyConfig()

  const students = studentsData?.students || []
  const activeStudents = students.filter((s) => s.is_active)

  // Calcular estudiantes nuevos (últimos 7 días)
  const newStudentsThisWeek = students.filter((s) => {
    const createdAt = new Date(s.created_at)
    const weekAgo = new Date()
    weekAgo.setDate(weekAgo.getDate() - 7)
    return createdAt >= weekAgo
  }).length

  // Obtener entrenamientos de hoy
  const today = new Date().getDay() // 0=Domingo, 6=Sábado
  const todayConfig = weeklyConfig?.configs.find((c) => c.weekday === today)

  if (loadingStudents || loadingConfig) {
    return <DashboardSkeleton />
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      <div className="max-w-7xl mx-auto p-6">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            Dashboard EntrenaSmart
          </h1>
          <p className="text-gray-600">
            Bienvenido al panel de control. Aquí tienes un resumen de tu actividad.
          </p>
        </div>

        {/* Métricas principales */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <MetricCard
            title="Total Estudiantes"
            value={students.length}
            subtitle={`${activeStudents.length} activos`}
            icon={<Users className="w-8 h-8" />}
            color="bg-gradient-to-br from-blue-500 to-blue-600"
          />
          <MetricCard
            title="Nuevos esta semana"
            value={newStudentsThisWeek}
            subtitle="últimos 7 días"
            icon={<TrendingUp className="w-8 h-8" />}
            color="bg-gradient-to-br from-green-500 to-green-600"
          />
          <MetricCard
            title="Sesiones configuradas"
            value={weeklyConfig?.configs.filter((c) => c.is_active).length || 0}
            subtitle="días de la semana"
            icon={<Calendar className="w-8 h-8" />}
            color="bg-gradient-to-br from-orange-500 to-orange-600"
          />
        </div>

        {/* Sección de entrenamientos de hoy */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center gap-3 mb-4">
              <Clock className="w-6 h-6 text-orange-500" />
              <h2 className="text-2xl font-bold">Entrenamiento de Hoy</h2>
            </div>

            {todayConfig && todayConfig.is_active ? (
              <div className="space-y-3">
                <div className="flex items-center justify-between p-4 bg-orange-50 rounded-lg border border-orange-200">
                  <div>
                    <p className="font-semibold text-lg">{todayConfig.session_type}</p>
                    <p className="text-sm text-gray-600">
                      📍 {todayConfig.location}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-2xl font-bold text-orange-600">
                      {todayConfig.weekday_name}
                    </p>
                  </div>
                </div>
                <p className="text-sm text-gray-500">
                  Los estudiantes recibirán recordatorios automáticos 30 min antes.
                </p>
              </div>
            ) : (
              <div className="text-center py-8 text-gray-400">
                <Calendar className="w-12 h-12 mx-auto mb-2 opacity-50" />
                <p>No hay entrenamientos configurados para hoy</p>
              </div>
            )}
          </div>

          {/* Acciones rápidas */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center gap-3 mb-4">
              <Settings className="w-6 h-6 text-blue-500" />
              <h2 className="text-2xl font-bold">Acciones Rápidas</h2>
            </div>

            <div className="space-y-3">
              <Link to="/students">
                <Button variant="primary" className="w-full justify-start gap-3">
                  <Users className="w-5 h-5" />
                  Gestionar Estudiantes
                </Button>
              </Link>

              <Link to="/config">
                <Button variant="secondary" className="w-full justify-start gap-3">
                  <Calendar className="w-5 h-5" />
                  Configurar Entrenamientos
                </Button>
              </Link>

              <Button variant="ghost" className="w-full justify-start gap-3" disabled>
                <Plus className="w-5 h-5" />
                Generar Reporte (Próximamente)
              </Button>
            </div>
          </div>
        </div>

        {/* Vista semanal */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-2xl font-bold mb-4">Vista Semanal</h2>
          <WeeklyView configs={weeklyConfig?.configs || []} />
        </div>
      </div>
    </div>
  )
}

/**
 * MetricCard - Tarjeta de métrica con icono
 */
interface MetricCardProps {
  title: string
  value: number
  subtitle: string
  icon: React.ReactNode
  color: string
}

function MetricCard({ title, value, subtitle, icon, color }: MetricCardProps) {
  return (
    <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
      <div className="flex items-center justify-between mb-4">
        <div className={`p-3 rounded-lg text-white ${color}`}>{icon}</div>
      </div>
      <h3 className="text-gray-600 text-sm font-medium mb-1">{title}</h3>
      <p className="text-4xl font-bold text-gray-900 mb-1">{value}</p>
      <p className="text-sm text-gray-500">{subtitle}</p>
    </div>
  )
}

/**
 * WeeklyView - Vista de la semana con entrenamientos configurados
 */
function WeeklyView({ configs }: { configs: any[] }) {
  const weekDays = ['Domingo', 'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado']

  return (
    <div className="grid grid-cols-7 gap-2">
      {configs.map((config) => {
        const isActive = config.is_active
        return (
          <div
            key={config.weekday}
            className={`p-3 rounded-lg border-2 transition-all ${
              isActive
                ? 'bg-orange-50 border-orange-300 hover:border-orange-400'
                : 'bg-gray-50 border-gray-200'
            }`}
          >
            <p className="text-xs font-semibold text-gray-700 mb-1">
              {weekDays[config.weekday].substring(0, 3)}
            </p>
            {isActive ? (
              <>
                <p className="text-sm font-bold text-orange-700 truncate">
                  {config.session_type}
                </p>
                <p className="text-xs text-gray-500 truncate">{config.location}</p>
              </>
            ) : (
              <p className="text-xs text-gray-400 italic">Sin config</p>
            )}
          </div>
        )
      })}
    </div>
  )
}

/**
 * DashboardSkeleton - Loading skeleton para el dashboard
 */
function DashboardSkeleton() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      <div className="max-w-7xl mx-auto p-6">
        <div className="mb-8">
          <Skeleton variant="text" width="300px" height="36px" className="mb-2" />
          <Skeleton variant="text" width="400px" height="20px" />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          {Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="bg-white rounded-lg shadow-md p-6">
              <Skeleton variant="circular" width="48px" height="48px" className="mb-4" />
              <Skeleton variant="text" width="120px" height="14px" className="mb-2" />
              <Skeleton variant="text" width="80px" height="36px" className="mb-2" />
              <Skeleton variant="text" width="100px" height="14px" />
            </div>
          ))}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {Array.from({ length: 2 }).map((_, i) => (
            <div key={i} className="bg-white rounded-lg shadow-md p-6">
              <Skeleton variant="text" width="200px" height="24px" className="mb-4" />
              <div className="space-y-3">
                <Skeleton variant="rectangular" width="100%" height="60px" />
                <Skeleton variant="rectangular" width="100%" height="60px" />
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
