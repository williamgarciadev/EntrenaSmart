import { useState } from 'react'
import {
  Users,
  Plus,
  Trash2,
  Edit,
} from 'lucide-react'
import {
  useStudents,
  useCreateStudent,
  useUpdateStudent,
  useDeleteStudent,
} from '@/hooks/useStudents'
import { useToast } from '@/components/Toast'
import { Button } from '@/components/ui/Button'
import type { Student } from '@/lib/api'

export default function StudentsPage() {
  const toast = useToast()
  const [isEditing, setIsEditing] = useState(false)
  const [editingId, setEditingId] = useState<number | null>(null)
  const [formData, setFormData] = useState({
    name: '',
    telegram_username: '',
    is_active: true,
  })

  const { data: studentsData, isLoading, isError } = useStudents()
  const createMutation = useCreateStudent()
  const updateMutation = useUpdateStudent()
  const deleteMutation = useDeleteStudent()

  const handleEdit = (student: Student) => {
    setEditingId(student.id)
    setFormData({
      name: student.name,
      telegram_username: student.telegram_username || '',
      is_active: student.is_active,
    })
    setIsEditing(true)
  }

  const handleSave = async () => {
    if (!formData.name.trim()) {
      toast.addToast({
        type: 'warning',
        title: 'Nombre requerido',
        description: 'Por favor ingresa el nombre del estudiante',
      })
      return
    }

    try {
      if (editingId) {
        await updateMutation.mutateAsync({
          studentId: editingId,
          data: formData,
        })
      } else {
        await createMutation.mutateAsync(formData)
      }

      setIsEditing(false)
      setEditingId(null)
      setFormData({
        name: '',
        telegram_username: '',
        is_active: true,
      })

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
                      setFormData({
                        name: '',
                        telegram_username: '',
                        is_active: true,
                      })
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

                <div className="space-y-4">
                  {/* Nombre */}
                  <div>
                    <label className="block text-sm font-medium text-foreground mb-1">
                      Nombre
                    </label>
                    <input
                      type="text"
                      value={formData.name}
                      onChange={(e) =>
                        setFormData((prev) => ({ ...prev, name: e.target.value }))
                      }
                      placeholder="Ej: Juan García"
                      className="w-full px-3 py-2 border border-border rounded-lg bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
                    />
                  </div>

                  {/* Usuario Telegram */}
                  <div>
                    <label className="block text-sm font-medium text-foreground mb-1">
                      Usuario Telegram (opcional)
                    </label>
                    <input
                      type="text"
                      value={formData.telegram_username}
                      onChange={(e) =>
                        setFormData((prev) => ({ ...prev, telegram_username: e.target.value }))
                      }
                      placeholder="Ej: juangarcia"
                      className="w-full px-3 py-2 border border-border rounded-lg bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
                    />
                    <p className="text-xs text-muted-foreground mt-1">
                      Sin la arroba (@). Se usa para vincular con Telegram.
                    </p>
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
                      <span className="text-sm text-foreground">Activo</span>
                    </label>
                  </div>

                  {/* Botones */}
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
                          name: '',
                          telegram_username: '',
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
