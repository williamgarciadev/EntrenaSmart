import { Dumbbell } from 'lucide-react'
import { ConfigWeekCalendar } from '@/components/features/ConfigWeekCalendar'

export function ConfigPage() {
  return (
    <div className="min-h-screen bg-background">
      <div className="max-w-4xl mx-auto py-8 px-4">
        {/* Encabezado mejorado */}
        <div className="mb-8 flex items-start gap-4">
          <div className="p-3 bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg text-white shadow-lg">
            <Dumbbell className="w-8 h-8" />
          </div>
          <div className="flex-1">
            <h1 className="text-4xl font-bold text-foreground mb-2">
              Configuración de Entrenamientos
            </h1>
            <p className="text-muted-foreground max-w-2xl">
              Configura los entrenamientos de tu semana. Los estudiantes recibirán recordatorios automáticos en los horarios que definas.
            </p>
          </div>
        </div>

        <ConfigWeekCalendar />
      </div>
    </div>
  )
}
