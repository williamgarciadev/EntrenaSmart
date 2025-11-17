import { Router, Route } from 'wouter'
import { QueryClientProvider, QueryClient } from '@tanstack/react-query'
import { ConfigPage } from './pages/ConfigPage'
import DashboardPage from './pages/DashboardPage'
import StudentsPage from './pages/StudentsPage'
import { Navigation } from './components/layout/Navigation'
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
        <Navigation />
        <Route path="/" component={DashboardPage} />
        <Route path="/students" component={StudentsPage} />
        <Route path="/config" component={ConfigPage} />
        <Route component={NotFound} />
      </Router>
    </QueryClientProvider>
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
