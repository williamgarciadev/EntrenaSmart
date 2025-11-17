/**
 * Hook personalizado para trabajar con programaciones de envío.
 *
 * Usa TanStack Query para manejo de estado del servidor.
 */
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { schedulesAPI, type MessageSchedule } from '@/lib/api'

/**
 * Hook para listar todas las programaciones
 */
export function useSchedules() {
  return useQuery({
    queryKey: ['schedules'],
    queryFn: () => schedulesAPI.listSchedules(),
    staleTime: 1000 * 60 * 5, // 5 minutos
  })
}

/**
 * Hook para listar solo programaciones activas
 */
export function useActiveSchedules() {
  return useQuery({
    queryKey: ['schedules', 'active'],
    queryFn: () => schedulesAPI.listSchedules(true),
    staleTime: 1000 * 60 * 5, // 5 minutos
  })
}

/**
 * Hook para obtener una programación específica
 */
export function useSchedule(scheduleId: number) {
  return useQuery({
    queryKey: ['schedules', scheduleId],
    queryFn: () => schedulesAPI.getSchedule(scheduleId),
    enabled: scheduleId > 0,
  })
}

/**
 * Hook para crear una nueva programación
 */
export function useCreateSchedule() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: {
      template_id: number
      student_id: number
      hour: number
      minute: number
      days_of_week: number[]
      is_active?: boolean
    }) => schedulesAPI.createSchedule(data),

    onSuccess: () => {
      // Invalidar lista de programaciones
      queryClient.invalidateQueries({
        queryKey: ['schedules'],
      })
      queryClient.invalidateQueries({
        queryKey: ['schedules', 'active'],
      })
    },
  })
}

/**
 * Hook para actualizar una programación
 */
export function useUpdateSchedule() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({
      scheduleId,
      data,
    }: {
      scheduleId: number
      data: Partial<{
        template_id: number
        student_id: number
        hour: number
        minute: number
        days_of_week: number[]
        is_active: boolean
      }>
    }) => schedulesAPI.updateSchedule(scheduleId, data),

    onSuccess: (_, variables) => {
      // Invalidar programación específica y lista
      queryClient.invalidateQueries({
        queryKey: ['schedules'],
      })
      queryClient.invalidateQueries({
        queryKey: ['schedules', variables.scheduleId],
      })
      queryClient.invalidateQueries({
        queryKey: ['schedules', 'active'],
      })
    },
  })
}

/**
 * Hook para eliminar una programación
 */
export function useDeleteSchedule() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (scheduleId: number) => schedulesAPI.deleteSchedule(scheduleId),

    onSuccess: (_, scheduleId) => {
      // Invalidar programación eliminada y lista
      queryClient.invalidateQueries({
        queryKey: ['schedules'],
      })
      queryClient.removeQueries({
        queryKey: ['schedules', scheduleId],
      })
      queryClient.invalidateQueries({
        queryKey: ['schedules', 'active'],
      })
    },
  })
}

/**
 * Hook para enviar mensaje de prueba
 */
export function useTestSchedule(scheduleId: number) {
  return useMutation({
    mutationFn: () => schedulesAPI.testSchedule(scheduleId),
  })
}
