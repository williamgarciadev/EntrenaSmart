import { useState } from 'react'
import {
  Clock,
  Plus,
  Trash2,
  Play,
} from 'lucide-react'
import {
  useSchedules,
  useCreateSchedule,
  useUpdateSchedule,
  useDeleteSchedule,
  useTestSchedule,
} from '@/hooks/useSchedules'
import { useTemplates } from '@/hooks/useTemplates'
import { useToast } from '@/components/Toast'
import { Button } from '@/components/ui/Button'
import type { MessageSchedule, Template } from '@/lib/api'

// Datos simulados para estudiantes
const MOCK_STUDENTS = [
  { id: 1, name: 'Juan García' },
  { id: 2, name: 'María López' },
  { id: 3, name: 'Carlos Rodríguez' },
  { id: 4, name: 'Ana Martínez' },
]

const DAYS_OF_WEEK = [
  { id: 0, name: 'Lunes' },
  { id: 1, name: 'Martes' },
  { id: 2, name: 'Miércoles' },
  { id: 3, name: 'Jueves' },
  { id: 4, name: 'Viernes' },
  { id: 5, name: 'Sábado' },
  { id: 6, name: 'Domingo' },
]

export default function SchedulesPage() {
  const toast = useToast()
  const [isEditing, setIsEditing] = useState(false)
  const [editingId, setEditingId] = useState<number | null>(null)
  const [formData, setFormData] = useState({
    template_id: 0,
    student_id: 0,
    hour: 9,
    minute: 0,
    days_of_week: [0, 1, 2, 3, 4] as number[],
    is_active: true,
  })

  const { data: schedulesData, isLoading, isError } = useSchedules()
  const { data: templatesData } = useTemplates()
  const createMutation = useCreateSchedule()
  const updateMutation = useUpdateSchedule()
  const deleteMutation = useDeleteSchedule()
  const testMutation = useTestSchedule(editingId || 0)

  const handleEdit = (schedule: MessageSchedule) => {
    setEditingId(schedule.id)
    setFormData({
      template_id: schedule.template_id,
      student_id: schedule.student_id,
      hour: schedule.hour,
      minute: schedule.minute,
      days_of_week: schedule.days_of_week,
      is_active: schedule.is_active,
    })
    setIsEditing(true)
  }

  const handleSave = async () => {
    if (!formData.template_id || !formData.student_id || formData.days_of_week.length === 0) {
      toast.addToast({
        type: 'warning',
        title: 'Campos incompletos',
        description: 'Por favor completa todos los campos requeridos',
      })
      return
    }

    try {
      if (editingId) {
        await updateMutation.mutateAsync({
          scheduleId: editingId,
          data: formData,
        })
      } else {
        await createMutation.mutateAsync(formData)
      }

      setIsEditing(false)
      setEditingId(null)
      setFormData({
        template_id: 0,
        student_id: 0,
        hour: 9,
        minute: 0,
        days_of_week: [0, 1, 2, 3, 4],
        is_active: true,
      })

      toast.addToast({
        type: 'success',
        title: editingId ? 'Programación actualizada' : 'Programación creada',
        description: 'Los cambios se han guardado correctamente',
      })
    } catch (error) {
      console.error('Error guardando programación:', error)
      toast.addToast({
        type: 'error',
        title: 'Error al guardar',
        description: 'Ocurrió un error al guardar la programación',
      })
    }
  }

  const handleDelete = async (id: number) => {
    if (!window.confirm('¿Estás seguro de que deseas eliminar esta programación?')) {
      return
    }

    try {
      await deleteMutation.mutateAsync(id)
      toast.addToast({
        type: 'success',
        title: 'Programación eliminada',
        description: 'La programación ha sido eliminada correctamente',
      })
    } catch (error) {
      console.error('Error eliminando programación:', error)
      toast.addToast({
        type: 'error',
        title: 'Error al eliminar',
        description: 'Ocurrió un error al eliminar la programación',
      })
    }
  }

  const handleTest = async () => {
    if (!editingId) return

    try {
      await testMutation.mutateAsync()
      toast.addToast({
        type: 'success',
        title: 'Mensaje de prueba enviado',
        description: 'El mensaje de prueba se envió exitosamente',
      })
    } catch (error) {
      console.error('Error enviando mensaje de prueba:', error)
      toast.addToast({
        type: 'error',
        title: 'Error al enviar prueba',
        description: 'Ocurrió un error al enviar el mensaje de prueba',
      })
    }
  }

  const toggleDay = (dayId: number) => {
    setFormData((prev) => {
      const days = prev.days_of_week
      if (days.includes(dayId)) {
        return {
          ...prev,
          days_of_week: days.filter((d) => d !== dayId),
        }
      } else {
        return {
          ...prev,
          days_of_week: [...days, dayId].sort((a, b) => a - b),
        }
      }
    })
  }

  const getTemplateName = (templateId: number) => {
    const template = templatesData?.templates.find((t: Template) => t.id === templateId)
    return template?.name || `Template ${templateId}`
  }

  const getStudentName = (studentId: number) => {
    const student = MOCK_STUDENTS.find((s) => s.id === studentId)
    return student?.name || `Estudiante ${studentId}`
  }

  const formatTime = (hour: number, minute: number) => {
    return `${String(hour).padStart(2, '0')}:${String(minute).padStart(2, '0')}`
  }

  if (isLoading)
    return (
      <div className="p-4">
        <p>Cargando programaciones...</p>
      </div>
    )

  if (isError)
    return (
      <div className="p-4 text-red-600">
        <p>Error al cargar las programaciones</p>
      </div>
    )

  const schedules = schedulesData?.schedules || []

  return (
    <div className="min-h-screen bg-background">
      <div className="max-w-6xl mx-auto p-6">
        {/* Encabezado mejorado */}
        <div className="mb-8 flex items-start gap-4">
          <div className="p-3 bg-gradient-to-br from-purple-500 to-purple-600 rounded-lg text-white shadow-lg">
            <Clock className="w-8 h-8" />
          </div>
          <div className="flex-1">
            <h1 className="text-4xl font-bold text-foreground mb-2">Programación de Envíos</h1>
            <p className="text-muted-foreground">
              Configura el envío automático de mensajes a estudiantes en horarios específicos. Define frecuencia, hora y destinatarios.
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Lista de programaciones */}
          <div className="lg:col-span-2">
            <div className="bg-card rounded-lg border border-border p-6">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-xl font-semibold text-foreground">Programaciones ({schedules.length})</h2>
                {!isEditing && (
                  <Button
                    onClick={() => {
                      setIsEditing(true)
                      setEditingId(null)
                      setFormData({
                        template_id: 0,
                        student_id: 0,
                        hour: 9,
                        minute: 0,
                        days_of_week: [0, 1, 2, 3, 4],
                        is_active: true,
                      })
                    }}
                    className="bg-primary text-primary-foreground hover:bg-primary/90 flex items-center gap-2"
                  >
                    <Plus className="w-4 h-4" />
                    Nueva Programación
                  </Button>
                )}
              </div>

              <div className="space-y-3">
                {schedules.map((schedule: MessageSchedule) => (
                  <div
                    key={schedule.id}
                    className={`p-4 border rounded-lg cursor-pointer transition ${
                      editingId === schedule.id
                        ? 'border-primary bg-primary/10'
                        : 'border-border hover:border-primary'
                    }`}
                    onClick={() => handleEdit(schedule)}
                  >
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <h3 className="font-medium text-foreground">
                          {getTemplateName(schedule.template_id)} → {getStudentName(schedule.student_id)}
                        </h3>
                        <p className="text-sm text-muted-foreground mt-1">
                          {formatTime(schedule.hour, schedule.minute)} • {schedule.days_of_week.length} días
                        </p>
                        <div className="flex flex-wrap gap-1 mt-2">
                          {schedule.days_of_week.map((dayId: number) => {
                            const dayName = DAYS_OF_WEEK.find((d) => d.id === dayId)?.name
                            return (
                              <span
                                key={dayId}
                                className="inline-block bg-accent/20 text-accent px-2 py-1 rounded text-xs"
                              >
                                {dayName}
                              </span>
                            )
                          })}
                        </div>
                      </div>
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          handleDelete(schedule.id)
                        }}
                        className="text-destructive hover:text-destructive/80 ml-2 p-1 hover:bg-red-50 rounded transition"
                        title="Eliminar programación"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                ))}

                {schedules.length === 0 && (
                  <p className="text-muted-foreground text-center py-8">
                    No hay programaciones. Crea una nueva para comenzar.
                  </p>
                )}
              </div>
            </div>
          </div>

          {/* Editor de programaciones */}
          {isEditing && (
            <div className="lg:col-span-1">
              <div className="bg-card rounded-lg border border-border p-6 sticky top-6">
                <h3 className="text-lg font-semibold text-foreground mb-4">
                  {editingId ? 'Editar Programación' : 'Nueva Programación'}
                </h3>

                <div className="space-y-4">
                  {/* Selector de plantilla */}
                  <div>
                    <label className="block text-sm font-medium text-foreground mb-1">
                      Plantilla
                    </label>
                    <select
                      value={formData.template_id}
                      onChange={(e) =>
                        setFormData((prev) => ({ ...prev, template_id: parseInt(e.target.value) }))
                      }
                      className="w-full px-3 py-2 border border-border rounded-lg bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
                    >
                      <option value={0}>Selecciona una plantilla</option>
                      {templatesData?.templates.map((template: Template) => (
                        <option key={template.id} value={template.id}>
                          {template.name}
                        </option>
                      ))}
                    </select>
                  </div>

                  {/* Selector de estudiante */}
                  <div>
                    <label className="block text-sm font-medium text-foreground mb-1">
                      Estudiante
                    </label>
                    <select
                      value={formData.student_id}
                      onChange={(e) =>
                        setFormData((prev) => ({ ...prev, student_id: parseInt(e.target.value) }))
                      }
                      className="w-full px-3 py-2 border border-border rounded-lg bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
                    >
                      <option value={0}>Selecciona un estudiante</option>
                      {MOCK_STUDENTS.map((student) => (
                        <option key={student.id} value={student.id}>
                          {student.name}
                        </option>
                      ))}
                    </select>
                  </div>

                  {/* Hora */}
                  <div className="grid grid-cols-2 gap-2">
                    <div>
                      <label className="block text-sm font-medium text-foreground mb-1">
                        Hora
                      </label>
                      <input
                        type="number"
                        min="0"
                        max="23"
                        value={formData.hour}
                        onChange={(e) =>
                          setFormData((prev) => ({ ...prev, hour: parseInt(e.target.value) }))
                        }
                        className="w-full px-3 py-2 border border-border rounded-lg bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-foreground mb-1">
                        Minuto
                      </label>
                      <input
                        type="number"
                        min="0"
                        max="59"
                        step="5"
                        value={formData.minute}
                        onChange={(e) =>
                          setFormData((prev) => ({ ...prev, minute: parseInt(e.target.value) }))
                        }
                        className="w-full px-3 py-2 border border-border rounded-lg bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
                      />
                    </div>
                  </div>

                  {/* Días de semana */}
                  <div>
                    <label className="block text-sm font-medium text-foreground mb-2">
                      Días de Semana
                    </label>
                    <div className="grid grid-cols-2 gap-2">
                      {DAYS_OF_WEEK.map((day) => (
                        <label key={day.id} className="flex items-center gap-2 cursor-pointer">
                          <input
                            type="checkbox"
                            checked={formData.days_of_week.includes(day.id)}
                            onChange={() => toggleDay(day.id)}
                            className="rounded border-border"
                          />
                          <span className="text-sm text-foreground">{day.name}</span>
                        </label>
                      ))}
                    </div>
                  </div>

                  {/* Estado */}
                  <div>
                    <label className="flex items-center gap-2 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={formData.is_active}
                        onChange={(e) =>
                          setFormData((prev) => ({ ...prev, is_active: e.target.checked }))
                        }
                        className="rounded border-border"
                      />
                      <span className="text-sm text-foreground">Activa</span>
                    </label>
                  </div>

                  {/* Botón de prueba */}
                  {editingId && (
                    <Button
                      onClick={handleTest}
                      variant="secondary"
                      className="w-full flex items-center justify-center gap-2"
                      disabled={testMutation.isPending}
                    >
                      <Play className="w-4 h-4" />
                      {testMutation.isPending ? 'Enviando...' : 'Enviar Prueba'}
                    </Button>
                  )}

                  {/* Botones de guardar/cancelar */}
                  <div className="flex gap-2">
                    <Button
                      onClick={handleSave}
                      className="flex-1 bg-primary text-primary-foreground hover:bg-primary/90"
                      disabled={createMutation.isPending || updateMutation.isPending}
                    >
                      {createMutation.isPending || updateMutation.isPending
                        ? 'Guardando...'
                        : 'Guardar'}
                    </Button>
                    <Button
                      onClick={() => {
                        setIsEditing(false)
                        setEditingId(null)
                        setFormData({
                          template_id: 0,
                          student_id: 0,
                          hour: 9,
                          minute: 0,
                          days_of_week: [0, 1, 2, 3, 4],
                          is_active: true,
                        })
                      }}
                      variant="secondary"
                      className="flex-1"
                    >
                      Cancelar
                    </Button>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
