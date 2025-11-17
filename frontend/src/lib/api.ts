/**
 * API Types y configuración
 */

const API_BASE_URL = '/api'
const AUTH_TOKEN = 'dev-secret-key'

// ============================================================================
// Configuración de fetch con autenticación
// ============================================================================

async function apiFetch<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${AUTH_TOKEN}`,
      ...options.headers,
    },
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Error desconocido' }))
    throw new Error(error.detail || `HTTP error! status: ${response.status}`)
  }

  return response.json()
}

// ============================================================================
// Student Types
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

// ============================================================================
// Template Types
// ============================================================================

export interface Template {
  id: number
  name: string
  content: string
  variables: string[]
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface TemplateCreate {
  name: string
  content: string
  variables?: string[]
  is_active?: boolean
}

export interface TemplateUpdate {
  name?: string
  content?: string
  variables?: string[]
  is_active?: boolean
}

export interface TemplateListResponse {
  templates: Template[]
  total: number
}

export interface TemplatePreviewResponse {
  preview_content: string
}

// ============================================================================
// Schedule Types
// ============================================================================

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
  template_name?: string
  student_name?: string
}

export interface ScheduleCreate {
  template_id: number
  student_id: number
  hour: number
  minute: number
  days_of_week: number[]
  is_active?: boolean
}

export interface ScheduleUpdate {
  template_id?: number
  student_id?: number
  hour?: number
  minute?: number
  days_of_week?: number[]
  is_active?: boolean
}

export interface ScheduleListResponse {
  schedules: MessageSchedule[]
  total: number
}

// ============================================================================
// Training Config Types
// ============================================================================

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
}

export interface TrainingDayConfigUpdate {
  session_type?: string
  location?: string
  is_active?: boolean
}

export interface WeeklyConfig {
  [weekday: number]: TrainingDayConfig
}

// ============================================================================
// Students API
// ============================================================================

export const studentsAPI = {
  async listStudents(activeOnly = false): Promise<StudentListResponse> {
    return apiFetch<StudentListResponse>(`/students?active_only=${activeOnly}`)
  },

  async getStudent(studentId: number): Promise<Student> {
    return apiFetch<Student>(`/students/${studentId}`)
  },

  async createStudent(data: StudentCreate): Promise<Student> {
    return apiFetch<Student>('/students', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  },

  async updateStudent(studentId: number, data: StudentUpdate): Promise<Student> {
    return apiFetch<Student>(`/students/${studentId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    })
  },

  async deleteStudent(studentId: number): Promise<{ message: string }> {
    return apiFetch<{ message: string }>(`/students/${studentId}`, {
      method: 'DELETE',
    })
  },
}

// ============================================================================
// Templates API
// ============================================================================

export const templatesAPI = {
  async listTemplates(activeOnly = false): Promise<TemplateListResponse> {
    return apiFetch<TemplateListResponse>(`/templates?active_only=${activeOnly}`)
  },

  async getTemplate(templateId: number): Promise<Template> {
    return apiFetch<Template>(`/templates/${templateId}`)
  },

  async createTemplate(data: TemplateCreate): Promise<Template> {
    return apiFetch<Template>('/templates', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  },

  async updateTemplate(templateId: number, data: TemplateUpdate): Promise<Template> {
    return apiFetch<Template>(`/templates/${templateId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    })
  },

  async deleteTemplate(templateId: number): Promise<{ message: string }> {
    return apiFetch<{ message: string }>(`/templates/${templateId}`, {
      method: 'DELETE',
    })
  },

  async previewTemplate(
    templateId: number,
    variablesValues: Record<string, string>
  ): Promise<TemplatePreviewResponse> {
    return apiFetch<TemplatePreviewResponse>(`/templates/${templateId}/preview`, {
      method: 'POST',
      body: JSON.stringify({ variables: variablesValues }),
    })
  },
}

// ============================================================================
// Schedules API
// ============================================================================

export const schedulesAPI = {
  async listSchedules(activeOnly = false): Promise<ScheduleListResponse> {
    return apiFetch<ScheduleListResponse>(`/schedules?active_only=${activeOnly}`)
  },

  async getSchedule(scheduleId: number): Promise<MessageSchedule> {
    return apiFetch<MessageSchedule>(`/schedules/${scheduleId}`)
  },

  async createSchedule(data: ScheduleCreate): Promise<MessageSchedule> {
    return apiFetch<MessageSchedule>('/schedules', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  },

  async updateSchedule(
    scheduleId: number,
    data: ScheduleUpdate
  ): Promise<MessageSchedule> {
    return apiFetch<MessageSchedule>(`/schedules/${scheduleId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    })
  },

  async deleteSchedule(scheduleId: number): Promise<{ message: string }> {
    return apiFetch<{ message: string }>(`/schedules/${scheduleId}`, {
      method: 'DELETE',
    })
  },

  async testSchedule(scheduleId: number): Promise<{ message: string }> {
    return apiFetch<{ message: string }>(`/schedules/${scheduleId}/test`, {
      method: 'POST',
    })
  },
}

// ============================================================================
// Training Config API
// ============================================================================

export const trainingConfigAPI = {
  async getWeeklyConfig(): Promise<WeeklyConfig> {
    return apiFetch<WeeklyConfig>('/training-config')
  },

  async getDayConfig(weekday: number): Promise<TrainingDayConfig> {
    return apiFetch<TrainingDayConfig>(`/training-config/${weekday}`)
  },

  async updateDayConfig(
    weekday: number,
    data: TrainingDayConfigCreate
  ): Promise<TrainingDayConfig> {
    return apiFetch<TrainingDayConfig>(`/training-config/${weekday}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    })
  },

  async deleteDayConfig(weekday: number): Promise<{ message: string }> {
    return apiFetch<{ message: string }>(`/training-config/${weekday}`, {
      method: 'DELETE',
    })
  },
}
