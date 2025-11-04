/** Main layout with sidebar and top bar */
import { Link, useLocation } from 'react-router-dom'

export default function Layout({ children }) {
  const location = useLocation()

  const navItems = [
    { path: '/', label: 'Streams', icon: '📹' },
    { path: '/alerts', label: 'Alerts', icon: '🚨' },
    { path: '/history', label: 'History', icon: '📊' },
    { path: '/settings', label: 'Settings', icon: '⚙️' },
  ]

  const isActive = (path) => location.pathname === path

  return (
    <div className="flex h-screen bg-[#0E0F11] text-[#D8D8D8]">
      {/* Left Sidebar */}
      <aside className="w-[260px] bg-[#1C1C1C] border-r border-white/5 flex flex-col">
        <div className="p-6 border-b border-white/5">
          <h1 className="text-xl font-bold text-white">Crowd Density</h1>
        </div>
        <nav className="flex-1 p-4 space-y-1">
          {navItems.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                isActive(item.path)
                  ? 'bg-emerald-500/20 text-emerald-400 ring-1 ring-emerald-400/30'
                  : 'text-[#D8D8D8] hover:bg-white/5'
              }`}
            >
              <span className="text-lg">{item.icon}</span>
              <span className="font-medium">{item.label}</span>
            </Link>
          ))}
        </nav>
        <div className="p-4 border-t border-white/5">
          <div className="px-4 py-2 text-sm text-gray-400">
            v0.1.0
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top Bar */}
        <header className="h-16 bg-[#1C1C1C] border-b border-white/5 flex items-center justify-between px-6">
          <div className="flex items-center gap-4 flex-1">
            <input
              type="search"
              placeholder="Search streams..."
              className="px-4 py-2 bg-[#0E0F11] border border-white/10 rounded-lg text-sm text-[#D8D8D8] placeholder-gray-500 focus:outline-none focus:ring-1 focus:ring-emerald-400/50 w-64"
            />
          </div>
          <div className="flex items-center gap-4">
            <button className="px-4 py-2 text-sm text-[#D8D8D8] hover:bg-white/5 rounded-lg transition-colors">
              User
            </button>
          </div>
        </header>

        {/* Content Area */}
        <main className="flex-1 overflow-y-auto p-6">
          {children}
        </main>
      </div>
    </div>
  )
}

