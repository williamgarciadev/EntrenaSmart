import { useState, useEffect } from 'react'
import { Bell, Calendar, Clock, Send, Users, Save } from 'lucide-react'
import {
  useWeeklyReminderConfig,
  useUpdateWeeklyReminder,
  useActiveStudents,
  useSendTestMessage,
} from '@/hooks/useWeeklyReminder'
import { useToast } from '@/components/Toast'
import { Button } from '@/components/ui/Button'

export function WeeklyReminderPage() {
  const toast = useToast()
  const { data: config, isLoading } = useWeeklyReminderConfig()
  const { data: studentsData } = useActiveStudents()
  const updateMutation = useUpdateWeeklyReminder()
  const testMutation = useSendTestMessage()

  const [formData, setFormData] = useState({
    is_monday_off: false,
    message_full_week: '',
    message_monday_off: '',
    send_day: 6,
    send_hour: 18,
    send_minute: 0,
    is_active: true,
  })

  // Cargar configuración cuando esté disponible
  useEffect(() => {
    if (config) {
      setFormData({
        is_monday_off: config.is_monday_off,
        message_full_week: config.message_full_week,
        message_monday_off: config.message_monday_off,
        send_day: config.send_day,
        send_hour: config.send_hour,
        send_minute: config.send_minute,
        is_active: config.is_active,
      })
    }
  }, [config])

  const handleSave = async () => {
    try {
      await updateMutation.mutateAsync(formData)
      toast.addToast({
        type: 'success',
        title: 'Configuración guardada',
        description: 'El recordatorio semanal se ha actualizado correctamente',
      })
    } catch (error) {
      console.error('Error guardando configuración:', error)
      toast.addToast({
        type: 'error',
        title: 'Error al guardar',
        description: 'Ocurrió un error al guardar la configuración',
      })
    }
  }

  const handleSendTest = async () => {
    try {
      await testMutation.mutateAsync()
      toast.addToast({
        type: 'success',
        title: 'Mensaje de prueba enviado',
        description: 'Revisa tu Telegram para ver el mensaje',
      })
    } catch (error) {
      console.error('Error enviando mensaje de prueba:', error)
      toast.addToast({
        type: 'error',
        title: 'Error al enviar',
        description: 'Ocurrió un error al enviar el mensaje de prueba',
      })
    }
  }

  const dayNames = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Cargando configuración...</p>
        </div>
      </div>
    )
  }

  const currentMessage = formData.is_monday_off
    ? formData.message_monday_off
    : formData.message_full_week

  return (
    <div className="min-h-screen bg-background">
      <div className="max-w-4xl mx-auto py-8 px-4">
        {/* Encabezado */}
        <div className="mb-8 flex items-start gap-4">
          <div className="p-3 bg-gradient-to-br from-purple-500 to-purple-600 rounded-lg text-white shadow-lg">
            <Bell className="w-8 h-8" />
          </div>
          <div className="flex-1">
            <h1 className="text-4xl font-bold text-foreground mb-2">
              Recordatorio Semanal
            </h1>
            <p className="text-muted-foreground max-w-2xl">
              Configura el mensaje automático que se envía a todos los alumnos activos para
              preguntarles cómo quieren programar su semana.
            </p>
          </div>
        </div>

        {/* Estadísticas */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
          <div className="bg-card border border-border rounded-lg p-4">
            <div className="flex items-center gap-3">
              <Users className="w-8 h-8 text-blue-500" />
              <div>
                <p className="text-sm text-muted-foreground">Alumnos Activos</p>
                <p className="text-2xl font-bold text-foreground">
                  {studentsData?.total || 0}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-card border border-border rounded-lg p-4">
            <div className="flex items-center gap-3">
              <Calendar className="w-8 h-8 text-purple-500" />
              <div>
                <p className="text-sm text-muted-foreground">Próximo Envío</p>
                <p className="text-2xl font-bold text-foreground">
                  {dayNames[formData.send_day]} {formData.send_hour}:{formData.send_minute.toString().padStart(2, '0')}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Configuración */}
        <div className="bg-card border border-border rounded-lg p-6 mb-6">
          <h2 className="text-xl font-semibold text-foreground mb-4">Configuración General</h2>

          {/* Estado */}
          <div className="mb-4">
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={formData.is_active}
                onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                className="w-4 h-4"
              />
              <span className="text-foreground">Recordatorio activo</span>
            </label>
            <p className="text-sm text-muted-foreground mt-1 ml-6">
              Si está activo, se enviará automáticamente cada semana
            </p>
          </div>

          {/* Modo lunes */}
          <div className="mb-6">
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={formData.is_monday_off}
                onChange={(e) => setFormData({ ...formData, is_monday_off: e.target.checked })}
                className="w-4 h-4"
              />
              <span className="text-foreground">El lunes no trabajo</span>
            </label>
            <p className="text-sm text-muted-foreground mt-1 ml-6">
              Cambia el mensaje para avisar que el lunes no estarás disponible
            </p>
          </div>

          {/* Programación */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-foreground mb-2">
                <Calendar className="w-4 h-4 inline mr-1" />
                Día de envío
              </label>
              <select
                value={formData.send_day}
                onChange={(e) => setFormData({ ...formData, send_day: Number(e.target.value) })}
                className="w-full px-3 py-2 bg-background border border-border rounded-md text-foreground"
              >
                {dayNames.map((day, index) => (
                  <option key={index} value={index}>{day}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-foreground mb-2">
                <Clock className="w-4 h-4 inline mr-1" />
                Hora
              </label>
              <input
                type="number"
                min="0"
                max="23"
                value={formData.send_hour}
                onChange={(e) => setFormData({ ...formData, send_hour: Number(e.target.value) })}
                className="w-full px-3 py-2 bg-background border border-border rounded-md text-foreground"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-foreground mb-2">
                Minuto
              </label>
              <input
                type="number"
                min="0"
                max="59"
                value={formData.send_minute}
                onChange={(e) => setFormData({ ...formData, send_minute: Number(e.target.value) })}
                className="w-full px-3 py-2 bg-background border border-border rounded-md text-foreground"
              />
            </div>
          </div>
        </div>

        {/* Mensajes */}
        <div className="bg-card border border-border rounded-lg p-6 mb-6">
          <h2 className="text-xl font-semibold text-foreground mb-4">Mensajes</h2>

          <div className="space-y-4">
            {/* Mensaje semana completa */}
            <div>
              <label className="block text-sm font-medium text-foreground mb-2">
                Mensaje - Semana Completa (Trabajo todos los días)
              </label>
              <textarea
                value={formData.message_full_week}
                onChange={(e) => setFormData({ ...formData, message_full_week: e.target.value })}
                rows={5}
                className="w-full px-3 py-2 bg-background border border-border rounded-md text-foreground font-mono text-sm"
                placeholder="Escribe el mensaje que se enviará cuando trabajes toda la semana..."
              />
            </div>

            {/* Mensaje lunes off */}
            <div>
              <label className="block text-sm font-medium text-foreground mb-2">
                Mensaje - Lunes OFF (No trabajo el lunes)
              </label>
              <textarea
                value={formData.message_monday_off}
                onChange={(e) => setFormData({ ...formData, message_monday_off: e.target.value })}
                rows={6}
                className="w-full px-3 py-2 bg-background border border-border rounded-md text-foreground font-mono text-sm"
                placeholder="Escribe el mensaje que se enviará cuando el lunes no trabajes..."
              />
            </div>
          </div>
        </div>

        {/* Vista previa */}
        <div className="bg-gradient-to-br from-blue-50 to-purple-50 dark:from-blue-950/20 dark:to-purple-950/20 border border-border rounded-lg p-6 mb-6">
          <h3 className="text-lg font-semibold text-foreground mb-3">
            📱 Vista Previa - Mensaje Actual
          </h3>
          <div className="bg-white dark:bg-gray-800 rounded-lg p-4 shadow-sm">
            <p className="text-sm text-muted-foreground mb-2">
              Modo: {formData.is_monday_off ? '🚫 Lunes OFF' : '✅ Semana Completa'}
            </p>
            <p className="text-foreground whitespace-pre-wrap font-mono text-sm">
              {currentMessage}
            </p>
          </div>
        </div>

        {/* Botones de acción */}
        <div className="flex gap-4">
          <Button
            onClick={handleSave}
            disabled={updateMutation.isPending}
            className="flex-1"
          >
            <Save className="w-4 h-4 mr-2" />
            {updateMutation.isPending ? 'Guardando...' : 'Guardar Configuración'}
          </Button>

          <Button
            onClick={handleSendTest}
            disabled={testMutation.isPending || !formData.is_active}
            variant="secondary"
          >
            <Send className="w-4 h-4 mr-2" />
            {testMutation.isPending ? 'Enviando...' : 'Enviar Prueba'}
          </Button>
        </div>

        {!formData.is_active && (
          <p className="text-sm text-amber-600 dark:text-amber-400 mt-2">
            ⚠️ El recordatorio está desactivado. Actívalo para poder enviar mensajes de prueba.
          </p>
        )}
      </div>
    </div>
  )
}
