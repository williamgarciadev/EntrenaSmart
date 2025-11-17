import { useState } from 'react'
import type { ReactNode } from 'react'
import { Navbar } from './Navbar'
import { Sidebar } from './Sidebar'

interface LayoutProps {
  children: ReactNode
}

export function Layout({ children }: LayoutProps) {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false)

  const closeSidebar = () => setIsSidebarOpen(false)
  const toggleSidebar = () => setIsSidebarOpen(!isSidebarOpen)

  return (
    <div className="min-h-screen bg-background flex flex-col">
      <Navbar onMenuToggle={toggleSidebar} isMenuOpen={isSidebarOpen} />
      <div className="flex flex-1">
        <Sidebar isOpen={isSidebarOpen} />
        <main className="flex-1 md:ml-0 w-full">
          <div
            onClick={closeSidebar}
            className="w-full"
          >
            {children}
          </div>
        </main>
      </div>
    </div>
  )
}
