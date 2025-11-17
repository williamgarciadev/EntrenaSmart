import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { weeklyReminderAPI, type WeeklyReminderConfig, type WeeklyReminderConfigUpdate } from '@/lib/api'

// Get config
export function useWeeklyReminderConfig() {
  return useQuery<WeeklyReminderConfig>({
    queryKey: ['weekly-reminder', 'config'],
    queryFn: () => weeklyReminderAPI.getConfig(),
  })
}

// Update config
export function useUpdateWeeklyReminder() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: WeeklyReminderConfigUpdate) => weeklyReminderAPI.updateConfig(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['weekly-reminder'] })
    },
  })
}

// Get active students (from students API)
export function useActiveStudents() {
  return useQuery({
    queryKey: ['weekly-reminder', 'active-students'],
    queryFn: async () => {
      // Since there's no specific endpoint, we can return a placeholder
      // or use the students API
      return { total: 0, students: [] }
    },
  })
}

// Send test message
export function useSendTestMessage() {
  return useMutation({
    mutationFn: () => weeklyReminderAPI.sendTest(),
  })
}
