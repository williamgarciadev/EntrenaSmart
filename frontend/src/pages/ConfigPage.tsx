import { ConfigWeekCalendar } from '@/components/features/ConfigWeekCalendar'

export function ConfigPage() {
  return (
    <div className="max-w-4xl mx-auto py-8 px-4">
      <div className="mb-8">
        <h1 className="text-4xl font-bold mb-2">Configuración de Entrenamientos</h1>
        <p className="text-gray-600">
          Configura los entrenamientos de tu semana. Los estudiantes recibirán recordatorios automáticos.
        </p>
      </div>

      <ConfigWeekCalendar />
    </div>
  )
}
