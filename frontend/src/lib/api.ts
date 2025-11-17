/**
 * API Types y configuración
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// ============================================================================
// STUDENTS
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

export const studentsAPI = {
  async listStudents(activeOnly = false): Promise<StudentListResponse> {
    const url = `${API_BASE_URL}/api/students${activeOnly ? '?active_only=true' : ''}`
    const response = await fetch(url, {
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
    })
    if (!response.ok) throw new Error('Failed to fetch students')
    return response.json()
  },

  async getStudent(id: number): Promise<Student> {
    const response = await fetch(`${API_BASE_URL}/api/students/${id}`, {
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
    })
    if (!response.ok) throw new Error('Failed to fetch student')
    return response.json()
  },

  async createStudent(data: StudentCreate): Promise<Student> {
    const response = await fetch(`${API_BASE_URL}/api/students`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify(data)
    })
    if (!response.ok) throw new Error('Failed to create student')
    return response.json()
  },

  async updateStudent(id: number, data: StudentUpdate): Promise<Student> {
    const response = await fetch(`${API_BASE_URL}/api/students/${id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify(data)
    })
    if (!response.ok) throw new Error('Failed to update student')
    return response.json()
  },

  async deleteStudent(id: number): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/api/students/${id}`, {
      method: 'DELETE',
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
    })
    if (!response.ok) throw new Error('Failed to delete student')
  }
}

// ============================================================================
// TEMPLATES
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

export const templatesAPI = {
  async listTemplates(activeOnly = false): Promise<TemplateListResponse> {
    const url = `${API_BASE_URL}/api/templates${activeOnly ? '?active_only=true' : ''}`
    const response = await fetch(url, {
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
    })
    if (!response.ok) throw new Error('Failed to fetch templates')
    return response.json()
  },

  async getTemplate(id: number): Promise<Template> {
    const response = await fetch(`${API_BASE_URL}/api/templates/${id}`, {
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
    })
    if (!response.ok) throw new Error('Failed to fetch template')
    return response.json()
  },

  async createTemplate(data: TemplateCreate): Promise<Template> {
    const response = await fetch(`${API_BASE_URL}/api/templates`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify(data)
    })
    if (!response.ok) throw new Error('Failed to create template')
    return response.json()
  },

  async updateTemplate(id: number, data: TemplateUpdate): Promise<Template> {
    const response = await fetch(`${API_BASE_URL}/api/templates/${id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify(data)
    })
    if (!response.ok) throw new Error('Failed to update template')
    return response.json()
  },

  async deleteTemplate(id: number): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/api/templates/${id}`, {
      method: 'DELETE',
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
    })
    if (!response.ok) throw new Error('Failed to delete template')
  }
}

// ============================================================================
// MESSAGE SCHEDULES
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

export const schedulesAPI = {
  async listSchedules(activeOnly = false): Promise<MessageScheduleListResponse> {
    const url = `${API_BASE_URL}/api/schedules${activeOnly ? '?active_only=true' : ''}`
    const response = await fetch(url, {
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
    })
    if (!response.ok) throw new Error('Failed to fetch schedules')
    return response.json()
  },

  async getSchedule(id: number): Promise<MessageSchedule> {
    const response = await fetch(`${API_BASE_URL}/api/schedules/${id}`, {
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
    })
    if (!response.ok) throw new Error('Failed to fetch schedule')
    return response.json()
  },

  async createSchedule(data: MessageScheduleCreate): Promise<MessageSchedule> {
    const response = await fetch(`${API_BASE_URL}/api/schedules`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify(data)
    })
    if (!response.ok) throw new Error('Failed to create schedule')
    return response.json()
  },

  async updateSchedule(id: number, data: MessageScheduleUpdate): Promise<MessageSchedule> {
    const response = await fetch(`${API_BASE_URL}/api/schedules/${id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify(data)
    })
    if (!response.ok) throw new Error('Failed to update schedule')
    return response.json()
  },

  async deleteSchedule(id: number): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/api/schedules/${id}`, {
      method: 'DELETE',
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
    })
    if (!response.ok) throw new Error('Failed to delete schedule')
  },

  async testSchedule(id: number): Promise<{ success: boolean; message: string }> {
    const response = await fetch(`${API_BASE_URL}/api/schedules/${id}/test`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
    })
    if (!response.ok) throw new Error('Failed to test schedule')
    return response.json()
  }
}

// ============================================================================
// TRAINING CONFIG
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

export interface WeeklyConfig {
  configs: TrainingDayConfig[]
  message: string
}

export const trainingConfigAPI = {
  async getWeeklyConfig(): Promise<WeeklyConfig> {
    const response = await fetch(`${API_BASE_URL}/api/training-config/weekly`, {
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
    })
    if (!response.ok) throw new Error('Failed to fetch weekly config')
    return response.json()
  },

  async updateDayConfig(data: TrainingDayConfigCreate): Promise<TrainingDayConfig> {
    const response = await fetch(`${API_BASE_URL}/api/training-config/day`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify(data)
    })
    if (!response.ok) throw new Error('Failed to update day config')
    return response.json()
  }
}
