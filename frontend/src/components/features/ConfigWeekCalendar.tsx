import { useState } from 'react'
import { useWeeklyConfig, useUpdateDayConfig } from '@/hooks/useTrainingConfig'
import { Button } from '@/components/ui/Button'

const TRAINING_TYPES = [
  'Pierna',
  'Funcional',
  'Brazo',
  'Espalda',
  'Pecho',
  'Hombros',
]

export function ConfigWeekCalendar() {
  const { data: weeklyConfig, isLoading } = useWeeklyConfig()
  const updateMutation = useUpdateDayConfig()
  const [editingDay, setEditingDay] = useState<number | null>(null)
  const [formData, setFormData] = useState({
    sessionType: '',
    location: '',
  })

  const handleEdit = (dayConfig: any) => {
    setEditingDay(dayConfig.weekday)
    setFormData({
      sessionType: dayConfig.session_type,
      location: dayConfig.location,
    })
  }

  const handleSave = async (weekday: number, weekdayName: string) => {
    await updateMutation.mutateAsync({
      weekday,
      data: {
        weekday,
        weekday_name: weekdayName,
        session_type: formData.sessionType,
        location: formData.location,
      },
    })
    setEditingDay(null)
    setFormData({ sessionType: '', location: '' })
  }

  const handleCancel = () => {
    setEditingDay(null)
    setFormData({ sessionType: '', location: '' })
  }

  if (isLoading) {
    return <div className="text-center py-8">Cargando configuración...</div>
  }

  if (!weeklyConfig) {
    return <div className="text-center py-8 text-red-500">Error al cargar configuración</div>
  }

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-bold">Configuración Semanal</h2>
      <p className="text-gray-600">Configure los entrenamientos de cada día de la semana</p>

      <div className="space-y-3">
        {weeklyConfig.configs.map((config) => (
          <DayConfigRow
            key={config.weekday}
            config={config}
            isEditing={editingDay === config.weekday}
            formData={formData}
            onEdit={() => handleEdit(config)}
            onSave={() => handleSave(config.weekday, config.weekday_name)}
            onCancel={handleCancel}
            onFormChange={(field, value) =>
              setFormData((prev) => ({ ...prev, [field]: value }))
            }
            isLoading={updateMutation.isPending}
          />
        ))}
      </div>
    </div>
  )
}

interface DayConfigRowProps {
  config: any
  isEditing: boolean
  formData: { sessionType: string; location: string }
  onEdit: () => void
  onSave: () => void
  onCancel: () => void
  onFormChange: (field: string, value: string) => void
  isLoading: boolean
}

function DayConfigRow({
  config,
  isEditing,
  formData,
  onEdit,
  onSave,
  onCancel,
  onFormChange,
  isLoading,
}: DayConfigRowProps) {
  return (
    <div className="border rounded-lg p-4 bg-white hover:shadow-md transition-shadow">
      {!isEditing ? (
        <div className="flex items-center justify-between">
          <div className="flex-1">
            <p className="font-semibold text-lg">{config.weekday_name}</p>
            {config.is_active && (
              <p className="text-sm text-gray-600">
                {config.session_type} • {config.location}
              </p>
            )}
            {!config.is_active && (
              <p className="text-sm text-gray-400 italic">No configurado</p>
            )}
          </div>
          <Button variant="secondary" size="sm" onClick={onEdit}>
            Editar
          </Button>
        </div>
      ) : (
        <div className="space-y-3">
          <div>
            <label className="block text-sm font-medium mb-1">
              Tipo de entrenamiento
            </label>
            <select
              value={formData.sessionType}
              onChange={(e) => onFormChange('sessionType', e.target.value)}
              className="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
            >
              <option value="">Seleccionar tipo...</option>
              {TRAINING_TYPES.map((type) => (
                <option key={type} value={type}>
                  {type}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Ubicación</label>
            <input
              type="text"
              placeholder="Ej: 2do Piso, Sala 1, etc"
              value={formData.location}
              onChange={(e) => onFormChange('location', e.target.value)}
              className="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
            />
          </div>

          <div className="flex gap-2">
            <Button
              variant="primary"
              size="sm"
              onClick={onSave}
              isLoading={isLoading}
            >
              Guardar
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={onCancel}
              disabled={isLoading}
            >
              Cancelar
            </Button>
          </div>
        </div>
      )}
    </div>
  )
}
