import { Router, Route } from 'wouter'
import { QueryClientProvider, QueryClient } from '@tanstack/react-query'
import { ConfigPage } from './pages/ConfigPage'
import './App.css'

// Crear cliente de query
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 minutos
      gcTime: 1000 * 60 * 10, // 10 minutos (antiguamente cacheTime)
    },
  },
})

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <Route path="/config" component={ConfigPage} />
        <Route path="/" component={HomePage} />
        <Route component={NotFound} />
      </Router>
    </QueryClientProvider>
  )
}

function HomePage() {
  return (
    <div className="max-w-4xl mx-auto py-8 px-4">
      <h1 className="text-4xl font-bold mb-4">EntrenaSmart Backoffice</h1>
      <p className="text-gray-600 mb-6">
        Bienvenido al panel de administración de EntrenaSmart. Aquí puedes configurar
        entrenamientos, gestionar estudiantes y ver métricas.
      </p>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <a
          href="/config"
          className="p-6 border rounded-lg hover:shadow-lg transition-shadow"
        >
          <h2 className="text-xl font-semibold mb-2">Configuración Semanal</h2>
          <p className="text-gray-600">Configure los entrenamientos de cada día</p>
        </a>
      </div>
    </div>
  )
}

function NotFound() {
  return (
    <div className="max-w-4xl mx-auto py-8 px-4 text-center">
      <h1 className="text-2xl font-bold mb-4">404 - Página no encontrada</h1>
      <a href="/" className="text-blue-500 hover:underline">
        Volver al inicio
      </a>
    </div>
  )
}

export default App
