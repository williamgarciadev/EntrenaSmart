import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import {
  Users,
  Plus,
  Trash2,
  Edit,
  AlertCircle,
  ChevronDown,
  ChevronUp,
  Calendar,
  Clock,
  MapPin,
} from 'lucide-react'
import {
  useStudents,
  useCreateStudent,
  useUpdateStudent,
  useDeleteStudent,
  useStudentTrainings,
} from '@/hooks/useStudents'
import { useToast } from '@/components/Toast'
import { Button } from '@/components/ui/Button'
import type { Student } from '@/lib/api'
import { studentSchema, type StudentFormData } from '@/schemas/student'

export default function StudentsPage() {
  const toast = useToast()
  const [isEditing, setIsEditing] = useState(false)
  const [editingId, setEditingId] = useState<number | null>(null)
  const [expandedStudentId, setExpandedStudentId] = useState<number | null>(null)

  const { data: studentsData, isLoading, isError } = useStudents()
  const createMutation = useCreateStudent()
  const updateMutation = useUpdateStudent()
  const deleteMutation = useDeleteStudent()

  // ✅ React Hook Form con validación Zod
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isValid },
  } = useForm<StudentFormData>({
    resolver: zodResolver(studentSchema),
    mode: 'onChange', // Validar en tiempo real
    defaultValues: {
      name: '',
      telegram_username: '',
      is_active: true,
    },
  })

  const handleEdit = (student: Student) => {
    setEditingId(student.id)
    reset({
      name: student.name,
      telegram_username: student.telegram_username || '',
      is_active: student.is_active,
    })
    setIsEditing(true)
  }

  const onSubmit = async (data: StudentFormData) => {
    try {
      if (editingId) {
        await updateMutation.mutateAsync({
          studentId: editingId,
          data,
        })
      } else {
        await createMutation.mutateAsync(data)
      }

      setIsEditing(false)
      setEditingId(null)
      reset()

      toast.addToast({
        type: 'success',
        title: editingId ? 'Estudiante actualizado' : 'Estudiante creado',
        description: 'Los cambios se han guardado correctamente',
      })
    } catch (error) {
      console.error('Error guardando estudiante:', error)
      toast.addToast({
        type: 'error',
        title: 'Error al guardar',
        description: 'Ocurrió un error al guardar el estudiante',
      })
    }
  }

  const handleDelete = async (id: number) => {
    if (!window.confirm('¿Estás seguro de que deseas eliminar este estudiante?')) {
      return
    }

    try {
      await deleteMutation.mutateAsync(id)
      toast.addToast({
        type: 'success',
        title: 'Estudiante eliminado',
        description: 'El estudiante ha sido eliminado correctamente',
      })
    } catch (error) {
      console.error('Error eliminando estudiante:', error)
      toast.addToast({
        type: 'error',
        title: 'Error al eliminar',
        description: 'Ocurrió un error al eliminar el estudiante',
      })
    }
  }

  if (isLoading)
    return (
      <div className="p-4">
        <p>Cargando estudiantes...</p>
      </div>
    )

  if (isError)
    return (
      <div className="p-4 text-red-600">
        <p>Error al cargar los estudiantes</p>
      </div>
    )

  const students = studentsData?.students || []

  return (
    <div className="min-h-screen bg-background">
      <div className="max-w-6xl mx-auto p-6">
        {/* Encabezado mejorado */}
        <div className="mb-8 flex items-start gap-4">
          <div className="p-3 bg-gradient-to-br from-orange-500 to-orange-600 rounded-lg text-white shadow-lg">
            <Users className="w-8 h-8" />
          </div>
          <div className="flex-1">
            <h1 className="text-4xl font-bold text-foreground mb-2">Gestión de Estudiantes</h1>
            <p className="text-muted-foreground">
              Administra los estudiantes inscritos en el programa de entrenamientos. Vincula con Telegram para envíos automáticos.
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Lista de estudiantes */}
          <div className="lg:col-span-2">
            <div className="bg-card rounded-lg border border-border p-6">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-xl font-semibold text-foreground">Estudiantes ({students.length})</h2>
                {!isEditing && (
                  <Button
                    onClick={() => {
                      setIsEditing(true)
                      setEditingId(null)
                      reset()
                    }}
                    className="bg-primary text-primary-foreground hover:bg-primary/90 flex items-center gap-2"
                  >
                    <Plus className="w-4 h-4" />
                    Nuevo Estudiante
                  </Button>
                )}
              </div>

              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-border">
                      <th className="text-left py-3 px-4 font-medium text-foreground">Nombre</th>
                      <th className="text-left py-3 px-4 font-medium text-foreground">Usuario Telegram</th>
                      <th className="text-left py-3 px-4 font-medium text-foreground">Chat ID</th>
                      <th className="text-left py-3 px-4 font-medium text-foreground">Estado</th>
                      <th className="text-right py-3 px-4 font-medium text-foreground">Acciones</th>
                    </tr>
                  </thead>
                  <tbody>
                    {students.map((student: Student) => (
                      <>
                        <tr
                          key={student.id}
                          className={`border-b border-border hover:bg-accent/5 transition ${
                            editingId === student.id ? 'bg-primary/10' : ''
                          }`}
                        >
                          <td className="py-3 px-4 text-foreground">{student.name}</td>
                          <td className="py-3 px-4 text-muted-foreground">
                            {student.telegram_username ? `@${student.telegram_username}` : '-'}
                          </td>
                          <td className="py-3 px-4 text-muted-foreground">
                            {student.chat_id || '-'}
                          </td>
                          <td className="py-3 px-4">
                            <span
                              className={`inline-block px-2 py-1 rounded text-xs font-medium ${
                                student.is_active
                                  ? 'bg-green-100 text-green-800'
                                  : 'bg-red-100 text-red-800'
                              }`}
                            >
                              {student.is_active ? 'Activo' : 'Inactivo'}
                            </span>
                          </td>
                          <td className="py-3 px-4 text-right flex justify-end gap-2">
                            <button
                              onClick={() => setExpandedStudentId(
                                expandedStudentId === student.id ? null : student.id
                              )}
                              className="text-blue-600 hover:text-blue-800 p-1 hover:bg-blue-50 rounded transition"
                              title="Ver horarios"
                            >
                              {expandedStudentId === student.id ? (
                                <ChevronUp className="w-4 h-4" />
                              ) : (
                                <ChevronDown className="w-4 h-4" />
                              )}
                            </button>
                            <button
                              onClick={() => handleEdit(student)}
                              className="text-primary hover:text-primary/80 p-1 hover:bg-blue-50 rounded transition"
                              title="Editar estudiante"
                            >
                              <Edit className="w-4 h-4" />
                            </button>
                            <button
                              onClick={() => handleDelete(student.id)}
                              className="text-destructive hover:text-destructive/80 p-1 hover:bg-red-50 rounded transition"
                              title="Eliminar estudiante"
                            >
                              <Trash2 className="w-4 h-4" />
                            </button>
                          </td>
                        </tr>
                        {expandedStudentId === student.id && (
                          <tr key={`${student.id}-trainings`}>
                            <td colSpan={5} className="p-4 bg-gray-50">
                              <StudentTrainingsView studentId={student.id} />
                            </td>
                          </tr>
                        )}
                      </>
                    ))}
                  </tbody>
                </table>

                {students.length === 0 && (
                  <p className="text-muted-foreground text-center py-8">
                    No hay estudiantes. Crea uno nuevo para comenzar.
                  </p>
                )}
              </div>
            </div>
          </div>

          {/* Editor de estudiantes */}
          {isEditing && (
            <div className="lg:col-span-1">
              <div className="bg-card rounded-lg border border-border p-6 sticky top-6">
                <h3 className="text-lg font-semibold text-foreground mb-4">
                  {editingId ? 'Editar Estudiante' : 'Nuevo Estudiante'}
                </h3>

                <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
                  {/* Nombre */}
                  <div>
                    <label className="block text-sm font-medium text-foreground mb-1">
                      Nombre <span className="text-red-500">*</span>
                    </label>
                    <input
                      {...register('name')}
                      type="text"
                      placeholder="Ej: Juan García"
                      className={`w-full px-3 py-2 border rounded-lg bg-background text-foreground focus:outline-none focus:ring-2 transition ${
                        errors.name
                          ? 'border-red-500 focus:ring-red-500'
                          : 'border-border focus:ring-primary'
                      }`}
                    />
                    {errors.name && (
                      <p className="mt-1 text-sm text-red-600 flex items-center gap-1">
                        <AlertCircle className="w-4 h-4" />
                        {errors.name.message}
                      </p>
                    )}
                  </div>

                  {/* Usuario Telegram */}
                  <div>
                    <label className="block text-sm font-medium text-foreground mb-1">
                      Usuario Telegram (opcional)
                    </label>
                    <input
                      {...register('telegram_username')}
                      type="text"
                      placeholder="Ej: juangarcia"
                      className={`w-full px-3 py-2 border rounded-lg bg-background text-foreground focus:outline-none focus:ring-2 transition ${
                        errors.telegram_username
                          ? 'border-red-500 focus:ring-red-500'
                          : 'border-border focus:ring-primary'
                      }`}
                    />
                    {errors.telegram_username ? (
                      <p className="mt-1 text-sm text-red-600 flex items-center gap-1">
                        <AlertCircle className="w-4 h-4" />
                        {errors.telegram_username.message}
                      </p>
                    ) : (
                      <p className="text-xs text-muted-foreground mt-1">
                        Sin la arroba (@). Se usa para vincular con Telegram.
                      </p>
                    )}
                  </div>

                  {/* Estado */}
                  <div>
                    <label className="flex items-center gap-2 cursor-pointer">
                      <input
                        {...register('is_active')}
                        type="checkbox"
                        className="rounded border-border"
                      />
                      <span className="text-sm text-foreground">Activo</span>
                    </label>
                  </div>

                  {/* Botones */}
                  <div className="flex gap-2">
                    <Button
                      type="submit"
                      className="flex-1 bg-primary text-primary-foreground hover:bg-primary/90"
                      disabled={!isValid || createMutation.isPending || updateMutation.isPending}
                    >
                      {createMutation.isPending || updateMutation.isPending
                        ? 'Guardando...'
                        : 'Guardar'}
                    </Button>
                    <Button
                      type="button"
                      onClick={() => {
                        setIsEditing(false)
                        setEditingId(null)
                        reset()
                      }}
                      variant="secondary"
                      className="flex-1"
                    >
                      Cancelar
                    </Button>
                  </div>
                </form>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

function StudentTrainingsView({ studentId }: { studentId: number }) {
  const { data, isLoading, isError } = useStudentTrainings(studentId)

  if (isLoading) {
    return <div className="text-sm text-muted-foreground">Cargando horarios...</div>
  }

  if (isError) {
    return <div className="text-sm text-red-600">Error al cargar horarios</div>
  }

  if (!data || data.trainings.length === 0) {
    return (
      <div className="text-sm text-muted-foreground italic">
        No tiene entrenamientos programados
      </div>
    )
  }

  return (
    <div className="space-y-3">
      <h4 className="font-semibold text-foreground flex items-center gap-2">
        <Calendar className="w-4 h-4" />
        Horarios Programados ({data.total})
      </h4>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {data.trainings.map((training) => (
          <div
            key={training.id}
            className="bg-white border border-border rounded-lg p-3 hover:shadow-sm transition"
          >
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <Calendar className="w-4 h-4 text-blue-600" />
                  <span className="font-medium text-foreground">
                    {training.weekday_name}
                  </span>
                </div>
                <div className="flex items-center gap-2 text-sm text-muted-foreground mb-1">
                  <Clock className="w-3 h-3" />
                  <span>{training.time_str}</span>
                </div>
                {training.session_type && (
                  <div className="text-sm text-foreground font-medium">
                    {training.session_type}
                  </div>
                )}
                {training.location && (
                  <div className="flex items-center gap-1 text-xs text-muted-foreground mt-1">
                    <MapPin className="w-3 h-3" />
                    <span>{training.location}</span>
                  </div>
                )}
              </div>
              <span
                className={`inline-block px-2 py-1 rounded text-xs font-medium ${
                  training.is_active
                    ? 'bg-green-100 text-green-800'
                    : 'bg-gray-100 text-gray-800'
                }`}
              >
                {training.is_active ? 'Activo' : 'Inactivo'}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
