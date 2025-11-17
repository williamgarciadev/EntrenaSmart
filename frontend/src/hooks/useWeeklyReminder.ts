import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '@/lib/api'

export interface WeeklyReminderConfig {
  id: number
  is_monday_off: boolean
  message_full_week: string
  message_monday_off: string
  send_day: number
  send_day_name: string
  send_hour: number
  send_minute: number
  send_time: string
  is_active: boolean
  current_message: string
  created_at?: string
  updated_at?: string
}

export interface WeeklyReminderUpdateData {
  is_monday_off?: boolean
  message_full_week?: string
  message_monday_off?: string
  send_day?: number
  send_hour?: number
  send_minute?: number
  is_active?: boolean
}

// Get config
export function useWeeklyReminderConfig() {
  return useQuery<WeeklyReminderConfig>({
    queryKey: ['weekly-reminder', 'config'],
    queryFn: async () => {
      const response = await api.get('/weekly-reminders/config')
      return response.data
    },
  })
}

// Update config
export function useUpdateWeeklyReminder() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (data: WeeklyReminderUpdateData) => {
      const response = await api.put('/weekly-reminders/config', data)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['weekly-reminder'] })
    },
  })
}

// Preview message
export function usePreviewMessage() {
  return useQuery({
    queryKey: ['weekly-reminder', 'preview'],
    queryFn: async () => {
      const response = await api.get('/weekly-reminders/preview')
      return response.data
    },
  })
}

// Get active students
export function useActiveStudents() {
  return useQuery({
    queryKey: ['weekly-reminder', 'active-students'],
    queryFn: async () => {
      const response = await api.get('/weekly-reminders/active-students')
      return response.data
    },
  })
}

// Send test message
export function useSendTestMessage() {
  return useMutation({
    mutationFn: async () => {
      const response = await api.post('/weekly-reminders/send-test')
      return response.data
    },
  })
}
