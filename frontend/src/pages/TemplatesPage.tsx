import { useState } from 'react'
import {
  MessageSquare,
  Plus,
  Trash2,
  Eye,
  Copy,
} from 'lucide-react'
import {
  useTemplates,
  useCreateTemplate,
  useUpdateTemplate,
  useDeleteTemplate,
  useTemplatePreview,
} from '@/hooks/useTemplates'
import { useToast } from '@/components/Toast'
import { Button } from '@/components/ui/Button'
import type { Template } from '@/lib/api'

export default function TemplatesPage() {
  const toast = useToast()
  const [isEditing, setIsEditing] = useState(false)
  const [editingId, setEditingId] = useState<number | null>(null)
  const [showPreview, setShowPreview] = useState(false)
  const [previewValues, setPreviewValues] = useState<Record<string, string>>({})

  const [formData, setFormData] = useState({
    name: '',
    content: '',
    variables: [] as string[],
  })

  const { data, isLoading, isError } = useTemplates()
  const createMutation = useCreateTemplate()
  const updateMutation = useUpdateTemplate()
  const deleteMutation = useDeleteTemplate()
  const previewMutation = useTemplatePreview(editingId || 0)

  const handleEdit = (template: Template) => {
    setEditingId(template.id)
    setFormData({
      name: template.name,
      content: template.content,
      variables: template.variables,
    })
    setIsEditing(true)
  }

  const handleSave = async () => {
    if (!formData.name || !formData.content) {
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
          templateId: editingId,
          data: {
            name: formData.name,
            content: formData.content,
            variables: formData.variables,
          },
        })
      } else {
        await createMutation.mutateAsync({
          name: formData.name,
          content: formData.content,
          variables: formData.variables,
        })
      }

      setIsEditing(false)
      setEditingId(null)
      setFormData({ name: '', content: '', variables: [] })

      toast.addToast({
        type: 'success',
        title: editingId ? 'Plantilla actualizada' : 'Plantilla creada',
        description: 'Los cambios se han guardado correctamente',
      })
    } catch (error) {
      console.error('Error guardando plantilla:', error)
      toast.addToast({
        type: 'error',
        title: 'Error al guardar',
        description: 'Ocurrió un error al guardar la plantilla',
      })
    }
  }

  const handleDelete = async (id: number) => {
    if (!window.confirm('¿Estás seguro de que deseas eliminar esta plantilla?')) {
      return
    }

    try {
      await deleteMutation.mutateAsync(id)
      toast.addToast({
        type: 'success',
        title: 'Plantilla eliminada',
        description: 'La plantilla ha sido eliminada correctamente',
      })
    } catch (error) {
      console.error('Error eliminando plantilla:', error)
      toast.addToast({
        type: 'error',
        title: 'Error al eliminar',
        description: 'Ocurrió un error al eliminar la plantilla',
      })
    }
  }

  const handlePreview = async () => {
    if (!editingId) return

    try {
      await previewMutation.mutateAsync(previewValues)
      setShowPreview(true)
      toast.addToast({
        type: 'success',
        title: 'Vista previa generada',
        description: 'Se ha generado la vista previa exitosamente',
      })
    } catch (error) {
      console.error('Error generando preview:', error)
      toast.addToast({
        type: 'error',
        title: 'Error al generar vista previa',
        description: 'Ocurrió un error al generar la vista previa',
      })
    }
  }

  const extractVariables = (content: string) => {
    const regex = /\{(\w+)\}/g
    const matches = content.match(regex)
    if (!matches) return []
    return Array.from(new Set(matches.map((m) => m.slice(1, -1))))
  }

  const handleContentChange = (value: string) => {
    setFormData((prev) => ({
      ...prev,
      content: value,
      variables: extractVariables(value),
    }))
    setPreviewValues({})
  }

  if (isLoading)
    return (
      <div className="p-4">
        <p>Cargando plantillas...</p>
      </div>
    )

  if (isError)
    return (
      <div className="p-4 text-red-600">
        <p>Error al cargar las plantillas</p>
      </div>
    )

  const templates = data?.templates || []

  return (
    <div className="min-h-screen bg-background">
      <div className="max-w-6xl mx-auto p-6">
        {/* Encabezado mejorado */}
        <div className="mb-8 flex items-start gap-4">
          <div className="p-3 bg-gradient-to-br from-green-500 to-green-600 rounded-lg text-white shadow-lg">
            <MessageSquare className="w-8 h-8" />
          </div>
          <div className="flex-1">
            <h1 className="text-4xl font-bold text-foreground mb-2">Plantillas de Mensajes</h1>
            <p className="text-muted-foreground">
              Crea y gestiona plantillas reutilizables para tus mensajes automáticos. Utiliza variables dinámicas para personalizar contenido.
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Lista de plantillas */}
          <div className="lg:col-span-2">
            <div className="bg-card rounded-lg border border-border p-6">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-xl font-semibold text-foreground">Plantillas ({templates.length})</h2>
                {!isEditing && (
                  <Button
                    onClick={() => {
                      setIsEditing(true)
                      setEditingId(null)
                      setFormData({ name: '', content: '', variables: [] })
                      setPreviewValues({})
                    }}
                    className="bg-primary text-primary-foreground hover:bg-primary/90 flex items-center gap-2"
                  >
                    <Plus className="w-4 h-4" />
                    Nueva Plantilla
                  </Button>
                )}
              </div>

              <div className="space-y-3">
                {templates.map((template: Template) => (
                  <div
                    key={template.id}
                    className={`p-4 border rounded-lg cursor-pointer transition ${
                      editingId === template.id
                        ? 'border-primary bg-primary/10'
                        : 'border-border hover:border-primary'
                    }`}
                    onClick={() => handleEdit(template)}
                  >
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <h3 className="font-medium text-foreground">{template.name}</h3>
                        <p className="text-sm text-muted-foreground mt-1 truncate">
                          {template.content}
                        </p>
                        {template.variables.length > 0 && (
                          <div className="flex flex-wrap gap-1 mt-2">
                            {template.variables.map((v) => (
                              <span
                                key={v}
                                className="inline-block bg-accent/20 text-accent px-2 py-1 rounded text-xs"
                              >
                                {v}
                              </span>
                            ))}
                          </div>
                        )}
                      </div>
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          handleDelete(template.id)
                        }}
                        className="text-destructive hover:text-destructive/80 ml-2 p-1 hover:bg-red-50 rounded transition"
                        title="Eliminar plantilla"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                ))}

                {templates.length === 0 && (
                  <p className="text-muted-foreground text-center py-8">
                    No hay plantillas. Crea una nueva para comenzar.
                  </p>
                )}
              </div>
            </div>
          </div>

          {/* Editor de plantillas */}
          {isEditing && (
            <div className="lg:col-span-1">
              <div className="bg-card rounded-lg border border-border p-6 sticky top-6">
                <h3 className="text-lg font-semibold text-foreground mb-4">
                  {editingId ? 'Editar Plantilla' : 'Nueva Plantilla'}
                </h3>

                <div className="space-y-4">
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
                      placeholder="Ej: Recordatorio diario"
                      className="w-full px-3 py-2 border border-border rounded-lg bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-foreground mb-1">
                      Contenido del Mensaje
                    </label>
                    <textarea
                      value={formData.content}
                      onChange={(e) => handleContentChange(e.target.value)}
                      placeholder="Usa {variable} para variables dinámicas"
                      rows={6}
                      className="w-full px-3 py-2 border border-border rounded-lg bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
                    />
                  </div>

                  {formData.variables.length > 0 && (
                    <div>
                      <label className="block text-sm font-medium text-foreground mb-2">
                        Variables Detectadas
                      </label>
                      <div className="flex flex-wrap gap-2">
                        {formData.variables.map((v) => (
                          <span
                            key={v}
                            className="inline-block bg-accent/20 text-accent px-2 py-1 rounded text-xs"
                          >
                            {v}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Sección de preview */}
                  {formData.variables.length > 0 && (
                    <div>
                      <label className="block text-sm font-medium text-foreground mb-1">
                        Vista Previa
                      </label>
                      <div className="space-y-2">
                        {formData.variables.map((v) => (
                          <input
                            key={v}
                            type="text"
                            value={previewValues[v] || ''}
                            onChange={(e) =>
                              setPreviewValues((prev) => ({
                                ...prev,
                                [v]: e.target.value,
                              }))
                            }
                            placeholder={`Valor para {${v}}`}
                            className="w-full px-2 py-1 border border-border rounded bg-background text-foreground text-sm focus:outline-none focus:ring-2 focus:ring-primary"
                          />
                        ))}
                        <Button
                          onClick={handlePreview}
                          variant="secondary"
                          className="w-full"
                          disabled={
                            formData.variables.some(
                              (v) => !previewValues[v]
                            )
                          }
                        >
                          Generar Preview
                        </Button>
                      </div>

                      {showPreview && previewMutation.data && (
                        <div className="mt-3 p-3 bg-muted rounded-lg">
                          <p className="text-xs font-medium text-muted-foreground mb-1">
                            PREVIEW:
                          </p>
                          <p className="text-sm text-foreground">
                            {previewMutation.data.preview_content}
                          </p>
                        </div>
                      )}
                    </div>
                  )}

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
                        setFormData({ name: '', content: '', variables: [] })
                        setShowPreview(false)
                        setPreviewValues({})
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
