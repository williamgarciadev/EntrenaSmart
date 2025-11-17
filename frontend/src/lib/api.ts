/**
 * API Client para EntrenaSmart Backend
 *
 * Proporciona funciones para interactuar con el backend API REST.
 */

const API_BASE_URL = '/api'

// ============================================================================
// Tipos e Interfaces
// ============================================================================

export interface Student {
  id: number
  name: string
  telegram_username?: string | null
  chat_id?: number | null
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface StudentCreate {
  name: string
  telegram_username?: string
  is_active?: boolean
}

export interface StudentUpdate {
  name?: string
  telegram_username?: string | null
  is_active?: boolean
}

export interface StudentListResponse {
  students: Student[]
  total: number
}

export interface TrainingDayConfig {
  id: number
  weekday: number
  weekday_name: string
  session_type: string
  location: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface TrainingDayConfigCreate {
  weekday: number
  weekday_name: string
  session_type: string
  location: string
  is_active?: boolean
}

export interface WeeklyConfig {
  configs: TrainingDayConfig[]
}

export interface Template {
  id: number
  name: string
  content: string
  preview_content?: string
  variables?: string[]
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface TemplateCreate {
  name: string
  content: string
  is_active?: boolean
}

export interface TemplateUpdate {
  name?: string
  content?: string
  is_active?: boolean
}

export interface TemplateListResponse {
  templates: Template[]
  total: number
}

export interface MessageSchedule {
  id: number
  template_id: number
  student_id: number
  hour: number
  minute: number
  days_of_week: number[]
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface MessageScheduleCreate {
  template_id: number
  student_id: number
  hour: number
  minute: number
  days_of_week: number[]
  is_active?: boolean
}

export interface MessageScheduleUpdate {
  template_id?: number
  student_id?: number
  hour?: number
  minute?: number
  days_of_week?: number[]
  is_active?: boolean
}

export interface MessageScheduleListResponse {
  schedules: MessageSchedule[]
  total: number
}

// ============================================================================
// Utilidades HTTP
// ============================================================================

async function fetchAPI<T>(
  endpoint: string,
  options?: RequestInit
): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Error desconocido' }))
    throw new Error(error.detail || `HTTP ${response.status}`)
  }

  return response.json()
}

// ============================================================================
// Students API
// ============================================================================

export const studentsAPI = {
  listStudents: async (activeOnly = false): Promise<StudentListResponse> => {
    return fetchAPI<StudentListResponse>(`/students?active_only=${activeOnly}`)
  },

  getStudent: async (studentId: number): Promise<Student> => {
    return fetchAPI<Student>(`/students/${studentId}`)
  },

  createStudent: async (data: StudentCreate): Promise<Student> => {
    return fetchAPI<Student>('/students', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  },

  updateStudent: async (studentId: number, data: StudentUpdate): Promise<Student> => {
    return fetchAPI<Student>(`/students/${studentId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    })
  },

  deleteStudent: async (studentId: number): Promise<{ message: string }> => {
    return fetchAPI<{ message: string }>(`/students/${studentId}`, {
      method: 'DELETE',
    })
  },
}

// ============================================================================
// Training Config API
// ============================================================================

export const trainingConfigAPI = {
  getWeeklyConfig: async (): Promise<WeeklyConfig> => {
    return fetchAPI<WeeklyConfig>('/training-config')
  },

  getDayConfig: async (weekday: number): Promise<TrainingDayConfig> => {
    return fetchAPI<TrainingDayConfig>(`/training-config/${weekday}`)
  },

  updateDayConfig: async (
    weekday: number,
    data: Partial<TrainingDayConfigCreate>
  ): Promise<{ message: string; data: any }> => {
    return fetchAPI<{ message: string; data: any }>(`/training-config/${weekday}`, {
      method: 'POST',
      body: JSON.stringify(data),
    })
  },

  deleteDayConfig: async (weekday: number): Promise<{ message: string }> => {
    return fetchAPI<{ message: string }>(`/training-config/${weekday}`, {
      method: 'DELETE',
    })
  },
}

// ============================================================================
// Templates API
// ============================================================================

export const templatesAPI = {
  listTemplates: async (activeOnly = false): Promise<TemplateListResponse> => {
    return fetchAPI<TemplateListResponse>(`/templates?active_only=${activeOnly}`)
  },

  getTemplate: async (templateId: number): Promise<Template> => {
    return fetchAPI<Template>(`/templates/${templateId}`)
  },

  createTemplate: async (data: TemplateCreate): Promise<Template> => {
    return fetchAPI<Template>('/templates', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  },

  updateTemplate: async (templateId: number, data: TemplateUpdate): Promise<Template> => {
    return fetchAPI<Template>(`/templates/${templateId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    })
  },

  deleteTemplate: async (templateId: number): Promise<{ message: string }> => {
    return fetchAPI<{ message: string }>(`/templates/${templateId}`, {
      method: 'DELETE',
    })
  },

  testTemplate: async (templateId: number): Promise<{ success: boolean; message: string }> => {
    return fetchAPI<{ success: boolean; message: string }>(`/templates/${templateId}/test`, {
      method: 'POST',
    })
  },

  previewTemplate: async (templateId: number, data?: Record<string, any>): Promise<{ preview_content: string }> => {
    return fetchAPI<{ preview_content: string }>(`/templates/${templateId}/preview`, {
      method: 'POST',
      body: JSON.stringify(data || {}),
    })
  },
}

// ============================================================================
// Schedules API
// ============================================================================

export const schedulesAPI = {
  listSchedules: async (activeOnly = false): Promise<MessageScheduleListResponse> => {
    return fetchAPI<MessageScheduleListResponse>(`/schedules?active_only=${activeOnly}`)
  },

  getSchedule: async (scheduleId: number): Promise<MessageSchedule> => {
    return fetchAPI<MessageSchedule>(`/schedules/${scheduleId}`)
  },

  createSchedule: async (data: MessageScheduleCreate): Promise<MessageSchedule> => {
    return fetchAPI<MessageSchedule>('/schedules', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  },

  updateSchedule: async (
    scheduleId: number,
    data: MessageScheduleUpdate
  ): Promise<MessageSchedule> => {
    return fetchAPI<MessageSchedule>(`/schedules/${scheduleId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    })
  },

  deleteSchedule: async (scheduleId: number): Promise<{ message: string }> => {
    return fetchAPI<{ message: string }>(`/schedules/${scheduleId}`, {
      method: 'DELETE',
    })
  },

  testSchedule: async (scheduleId: number): Promise<{ success: boolean; message: string }> => {
    return fetchAPI<{ success: boolean; message: string }>(`/schedules/${scheduleId}/test`, {
      method: 'POST',
    })
  },
}
