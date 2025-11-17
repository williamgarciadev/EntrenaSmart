/**
 * API Types y configuración
 */

// ============================================================================
// Configuration
// ============================================================================

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
const DEV_TOKEN = import.meta.env.VITE_DEV_TOKEN || 'dev-token'

// ============================================================================
// Types - Students
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
  is_active: boolean
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
// Types - Templates
// ============================================================================

export interface Template {
  id: number
  name: string
  content: string
  variables?: string[]
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
// Types - Schedules
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
// Types - Training Config
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
  weekday?: number
  weekday_name?: string
  session_type?: string
  location?: string
}

export interface WeeklyConfig {
  configs: TrainingDayConfig[]
}

// ============================================================================
// API Helper Functions
// ============================================================================

async function fetchAPI<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`

  const headers = {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${DEV_TOKEN}`,
    ...options.headers,
  }

  const response = await fetch(url, {
    ...options,
    headers,
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({
      detail: 'Error desconocido'
    }))
    throw new Error(error.detail || `HTTP error! status: ${response.status}`)
  }

  return response.json()
}

// ============================================================================
// Students API
// ============================================================================

export const studentsAPI = {
  async listStudents(activeOnly = false): Promise<Student[]> {
    const params = activeOnly ? '?active_only=true' : ''
    const response = await fetchAPI<StudentListResponse>(`/api/students${params}`)
    return response.students
  },

  async getStudent(studentId: number): Promise<Student> {
    return fetchAPI<Student>(`/api/students/${studentId}`)
  },

  async createStudent(data: StudentCreate): Promise<Student> {
    return fetchAPI<Student>('/api/students', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  },

  async updateStudent(studentId: number, data: StudentUpdate): Promise<Student> {
    return fetchAPI<Student>(`/api/students/${studentId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    })
  },

  async deleteStudent(studentId: number): Promise<void> {
    await fetchAPI<void>(`/api/students/${studentId}`, {
      method: 'DELETE',
    })
  },
}

// ============================================================================
// Templates API
// ============================================================================

export const templatesAPI = {
  async listTemplates(activeOnly = false): Promise<Template[]> {
    const params = activeOnly ? '?active_only=true' : ''
    const response = await fetchAPI<TemplateListResponse>(`/api/templates${params}`)
    return response.templates
  },

  async getTemplate(templateId: number): Promise<Template> {
    return fetchAPI<Template>(`/api/templates/${templateId}`)
  },

  async createTemplate(data: TemplateCreate): Promise<Template> {
    return fetchAPI<Template>('/api/templates', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  },

  async updateTemplate(templateId: number, data: TemplateUpdate): Promise<Template> {
    return fetchAPI<Template>(`/api/templates/${templateId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    })
  },

  async deleteTemplate(templateId: number): Promise<void> {
    await fetchAPI<void>(`/api/templates/${templateId}`, {
      method: 'DELETE',
    })
  },

  async previewTemplate(
    templateId: number,
    variablesValues: Record<string, string>
  ): Promise<string> {
    const response = await fetchAPI<TemplatePreviewResponse>(
      `/api/templates/${templateId}/preview`,
      {
        method: 'POST',
        body: JSON.stringify(variablesValues),
      }
    )
    return response.preview_content
  },
}

// ============================================================================
// Schedules API
// ============================================================================

export const schedulesAPI = {
  async listSchedules(activeOnly = false): Promise<MessageSchedule[]> {
    const params = activeOnly ? '?active_only=true' : ''
    const response = await fetchAPI<MessageScheduleListResponse>(`/api/schedules${params}`)
    return response.schedules
  },

  async getSchedule(scheduleId: number): Promise<MessageSchedule> {
    return fetchAPI<MessageSchedule>(`/api/schedules/${scheduleId}`)
  },

  async createSchedule(data: MessageScheduleCreate): Promise<MessageSchedule> {
    return fetchAPI<MessageSchedule>('/api/schedules', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  },

  async updateSchedule(
    scheduleId: number,
    data: MessageScheduleUpdate
  ): Promise<MessageSchedule> {
    return fetchAPI<MessageSchedule>(`/api/schedules/${scheduleId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    })
  },

  async deleteSchedule(scheduleId: number): Promise<void> {
    await fetchAPI<void>(`/api/schedules/${scheduleId}`, {
      method: 'DELETE',
    })
  },

  async testSchedule(scheduleId: number): Promise<void> {
    await fetchAPI<void>(`/api/schedules/${scheduleId}/test`, {
      method: 'POST',
    })
  },
}

// ============================================================================
// Training Config API
// ============================================================================

export const trainingConfigAPI = {
  async getWeeklyConfig(): Promise<WeeklyConfig> {
    return fetchAPI<WeeklyConfig>('/api/training-config')
  },

  async getDayConfig(weekday: number): Promise<TrainingDayConfig> {
    return fetchAPI<TrainingDayConfig>(`/api/training-config/${weekday}`)
  },

  async updateDayConfig(
    weekday: number,
    data: TrainingDayConfigCreate
  ): Promise<TrainingDayConfig> {
    return fetchAPI<TrainingDayConfig>(`/api/training-config/${weekday}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    })
  },

  async deleteDayConfig(weekday: number): Promise<void> {
    await fetchAPI<void>(`/api/training-config/${weekday}`, {
      method: 'DELETE',
    })
  },
}
