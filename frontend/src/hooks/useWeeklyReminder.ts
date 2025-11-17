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

// Get active students
export function useActiveStudents() {
  return useQuery({
    queryKey: ['weekly-reminder', 'active-students'],
    queryFn: async () => {
      const response = await fetch('http://localhost:8000/api/weekly-reminders/active-students', {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
      })
      if (!response.ok) throw new Error('Failed to fetch active students')
      return response.json()
    },
  })
}

// Send test message
export function useSendTestMessage() {
  return useMutation({
    mutationFn: () => weeklyReminderAPI.sendTest(),
  })
}
