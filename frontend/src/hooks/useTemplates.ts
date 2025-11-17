/**
 * Hook personalizado para trabajar con plantillas de mensajes.
 *
 * Usa TanStack Query para manejo de estado del servidor.
 */
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { templatesAPI, type Template } from '@/lib/api'

/**
 * Hook para listar todas las plantillas
 */
export function useTemplates() {
  return useQuery({
    queryKey: ['templates'],
    queryFn: () => templatesAPI.listTemplates(),
    staleTime: 1000 * 60 * 5, // 5 minutos
  })
}

/**
 * Hook para listar solo plantillas activas
 */
export function useActiveTemplates() {
  return useQuery({
    queryKey: ['templates', 'active'],
    queryFn: () => templatesAPI.listTemplates(true),
    staleTime: 1000 * 60 * 5, // 5 minutos
  })
}

/**
 * Hook para obtener una plantilla específica
 */
export function useTemplate(templateId: number) {
  return useQuery({
    queryKey: ['templates', templateId],
    queryFn: () => templatesAPI.getTemplate(templateId),
    enabled: templateId > 0,
  })
}

/**
 * Hook para crear una nueva plantilla
 */
export function useCreateTemplate() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: {
      name: string
      content: string
      variables?: string[]
      is_active?: boolean
    }) => templatesAPI.createTemplate(data),

    onSuccess: () => {
      // Invalidar lista de plantillas
      queryClient.invalidateQueries({
        queryKey: ['templates'],
      })
      queryClient.invalidateQueries({
        queryKey: ['templates', 'active'],
      })
    },
  })
}

/**
 * Hook para actualizar una plantilla
 */
export function useUpdateTemplate() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({
      templateId,
      data,
    }: {
      templateId: number
      data: Partial<{
        name: string
        content: string
        variables: string[]
        is_active: boolean
      }>
    }) => templatesAPI.updateTemplate(templateId, data),

    onSuccess: (_, variables) => {
      // Invalidar plantilla específica y lista
      queryClient.invalidateQueries({
        queryKey: ['templates'],
      })
      queryClient.invalidateQueries({
        queryKey: ['templates', variables.templateId],
      })
      queryClient.invalidateQueries({
        queryKey: ['templates', 'active'],
      })
    },
  })
}

/**
 * Hook para eliminar una plantilla
 */
export function useDeleteTemplate() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (templateId: number) => templatesAPI.deleteTemplate(templateId),

    onSuccess: (_, templateId) => {
      // Invalidar plantilla eliminada y lista
      queryClient.invalidateQueries({
        queryKey: ['templates'],
      })
      queryClient.removeQueries({
        queryKey: ['templates', templateId],
      })
      queryClient.invalidateQueries({
        queryKey: ['templates', 'active'],
      })
    },
  })
}

/**
 * Hook para obtener preview de plantilla con variables reemplazadas
 */
export function useTemplatePreview(templateId: number) {
  return useMutation({
    mutationFn: (variablesValues: Record<string, string>) =>
      templatesAPI.previewTemplate(templateId, variablesValues),
  })
}
