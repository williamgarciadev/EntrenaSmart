/**
 * Hook personalizado para trabajar con estudiantes.
 *
 * Usa TanStack Query para manejo de estado del servidor.
 */
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { studentsAPI, type Student } from '@/lib/api'

/**
 * Hook para listar todos los estudiantes
 */
export function useStudents() {
  return useQuery({
    queryKey: ['students'],
    queryFn: () => studentsAPI.listStudents(),
    staleTime: 1000 * 60 * 5, // 5 minutos
  })
}

/**
 * Hook para listar solo estudiantes activos
 */
export function useActiveStudents() {
  return useQuery({
    queryKey: ['students', 'active'],
    queryFn: () => studentsAPI.listStudents(true),
    staleTime: 1000 * 60 * 5, // 5 minutos
  })
}

/**
 * Hook para obtener un estudiante específico
 */
export function useStudent(studentId: number) {
  return useQuery({
    queryKey: ['students', studentId],
    queryFn: () => studentsAPI.getStudent(studentId),
    enabled: studentId > 0,
  })
}

/**
 * Hook para crear un nuevo estudiante
 */
export function useCreateStudent() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: {
      name: string
      telegram_username?: string
      is_active?: boolean
    }) => studentsAPI.createStudent(data),

    onSuccess: () => {
      // Invalidar lista de estudiantes
      queryClient.invalidateQueries({
        queryKey: ['students'],
      })
      queryClient.invalidateQueries({
        queryKey: ['students', 'active'],
      })
    },
  })
}

/**
 * Hook para actualizar un estudiante
 */
export function useUpdateStudent() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({
      studentId,
      data,
    }: {
      studentId: number
      data: Partial<{
        name: string
        telegram_username: string
        is_active: boolean
      }>
    }) => studentsAPI.updateStudent(studentId, data),

    onSuccess: (_, variables) => {
      // Invalidar estudiante específico y lista
      queryClient.invalidateQueries({
        queryKey: ['students'],
      })
      queryClient.invalidateQueries({
        queryKey: ['students', variables.studentId],
      })
      queryClient.invalidateQueries({
        queryKey: ['students', 'active'],
      })
    },
  })
}

/**
 * Hook para eliminar un estudiante (soft delete)
 */
export function useDeleteStudent() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (studentId: number) => studentsAPI.deleteStudent(studentId),

    onSuccess: (_, studentId) => {
      // Invalidar estudiante eliminado y lista
      queryClient.invalidateQueries({
        queryKey: ['students'],
      })
      queryClient.removeQueries({
        queryKey: ['students', studentId],
      })
      queryClient.invalidateQueries({
        queryKey: ['students', 'active'],
      })
    },
  })
}
