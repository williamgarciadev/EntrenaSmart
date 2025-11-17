/**
 * Hook customizado para trabajar con la configuración de entrenamientos.
 *
 * Usa TanStack Query para manejo de estado del servidor.
 */
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { trainingConfigAPI, type TrainingDayConfig, type WeeklyConfig } from '@/lib/api'

/**
 * Hook para obtener la configuración semanal completa
 */
export function useWeeklyConfig() {
  return useQuery({
    queryKey: ['training-config'],
    queryFn: () => trainingConfigAPI.getWeeklyConfig(),
    staleTime: 1000 * 60 * 5, // 5 minutos
  })
}

/**
 * Hook para obtener la configuración de un día específico
 */
export function useDayConfig(weekday: number) {
  return useQuery({
    queryKey: ['training-config', weekday],
    queryFn: () => trainingConfigAPI.getDayConfig(weekday),
    enabled: weekday >= 0 && weekday <= 6,
  })
}

/**
 * Hook para actualizar la configuración de un día
 */
export function useUpdateDayConfig() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({
      weekday,
      data,
    }: {
      weekday: number
      data: {
        weekday: number
        weekday_name: string
        session_type: string
        location: string
      }
    }) => trainingConfigAPI.updateDayConfig(weekday, data),

    onSuccess: (_, variables) => {
      // Invalidar queries relacionadas
      queryClient.invalidateQueries({
        queryKey: ['training-config'],
      })
      queryClient.invalidateQueries({
        queryKey: ['training-config', variables.weekday],
      })
    },
  })
}

/**
 * Hook para eliminar la configuración de un día
 */
export function useDeleteDayConfig() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (weekday: number) =>
      trainingConfigAPI.deleteDayConfig(weekday),

    onSuccess: (_, weekday) => {
      // Invalidar queries relacionadas
      queryClient.invalidateQueries({
        queryKey: ['training-config'],
      })
      queryClient.invalidateQueries({
        queryKey: ['training-config', weekday],
      })
    },
  })
}
