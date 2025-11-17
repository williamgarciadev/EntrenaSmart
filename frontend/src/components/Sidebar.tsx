import { Home, Settings, MessageSquare, Clock, Users } from 'lucide-react'
import { useLocation } from 'wouter'
import type { ReactNode } from 'react'

interface NavItem {
  href: string
  label: string
  icon: ReactNode
}

interface SidebarProps {
  isOpen: boolean
}

export function Sidebar({ isOpen }: SidebarProps) {
  const [location] = useLocation()

  const navItems: NavItem[] = [
    {
      href: '/',
      label: 'Inicio',
      icon: <Home className="w-5 h-5" />,
    },
    {
      href: '/config',
      label: 'Configuración',
      icon: <Settings className="w-5 h-5" />,
    },
    {
      href: '/templates',
      label: 'Plantillas',
      icon: <MessageSquare className="w-5 h-5" />,
    },
    {
      href: '/schedules',
      label: 'Programación',
      icon: <Clock className="w-5 h-5" />,
    },
    {
      href: '/students',
      label: 'Estudiantes',
      icon: <Users className="w-5 h-5" />,
    },
  ]

  const isActive = (href: string) => {
    if (href === '/') {
      return location === '/'
    }
    return location.startsWith(href)
  }

  return (
    <>
      {/* Overlay móvil */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/20 z-30 md:hidden"
          style={{
            animation: 'fadeIn 0.2s ease-in-out',
          }}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`fixed left-0 top-0 h-screen w-64 bg-white border-r border-border z-40 transition-transform duration-300 ease-in-out md:translate-x-0 pt-16 ${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <nav className="p-4 space-y-2">
          {navItems.map((item) => {
            const active = isActive(item.href)
            return (
              <a
                key={item.href}
                href={item.href}
                className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                  active
                    ? 'bg-primary text-primary-foreground font-medium'
                    : 'text-foreground hover:bg-accent/10 text-muted-foreground hover:text-foreground'
                }`}
              >
                {item.icon}
                <span>{item.label}</span>
              </a>
            )
          })}
        </nav>
      </aside>
    </>
  )
}
