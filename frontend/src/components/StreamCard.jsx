/** Stream card component with live stats */
import { useNavigate } from 'react-router-dom'
import { useState, useEffect } from 'react'

export default function StreamCard({ stream }) {
  const navigate = useNavigate()
  const [showActions, setShowActions] = useState(false)

  const statusConfig = {
    running: {
      color: 'bg-emerald-500/20 text-emerald-400 ring-emerald-400/30',
      icon: (
        <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
          <circle cx="10" cy="10" r="3" />
        </svg>
      ),
    },
    starting: {
      color: 'bg-yellow-500/20 text-yellow-400 ring-yellow-400/30',
      icon: (
        <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
          <circle cx="10" cy="10" r="3" className="animate-pulse" />
        </svg>
      ),
    },
    stopped: {
      color: 'bg-gray-500/20 text-gray-400 ring-gray-400/30',
      icon: (
        <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
          <circle cx="10" cy="10" r="3" />
        </svg>
      ),
    },
    error: {
      color: 'bg-red-500/20 text-red-400 ring-red-400/30',
      icon: (
        <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
        </svg>
      ),
    },
  }

  const config = statusConfig[stream.status] || statusConfig.stopped

  return (
    <div
      className="group relative bg-gradient-to-br from-[#1C1C1C] to-[#0E0F11] border border-white/5 rounded-2xl p-6 cursor-pointer hover:border-emerald-400/30 hover:shadow-xl hover:shadow-emerald-500/10 transition-all duration-300"
      onMouseEnter={() => setShowActions(true)}
      onMouseLeave={() => setShowActions(false)}
      onClick={() => navigate(`/streams/${stream.id}`)}
    >
      {/* Quick Actions (on hover) */}
      {showActions && (
        <div className="absolute top-4 right-4 flex gap-2 z-10 animate-in fade-in slide-in-from-top-2 duration-200">
          <button
            onClick={(e) => {
              e.stopPropagation()
              navigate(`/streams/${stream.id}`)
            }}
            className="px-3 py-1.5 bg-emerald-500/20 text-emerald-400 text-xs rounded-lg hover:bg-emerald-500/30 transition-colors backdrop-blur-sm border border-emerald-500/20"
          >
            Open
          </button>
          <button
            onClick={(e) => {
              e.stopPropagation()
              navigate(`/streams/${stream.id}?edit=zones`)
            }}
            className="px-3 py-1.5 bg-blue-500/20 text-blue-400 text-xs rounded-lg hover:bg-blue-500/30 transition-colors backdrop-blur-sm border border-blue-500/20"
          >
            Zones
          </button>
        </div>
      )}

      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1 min-w-0">
          <h3 className="text-lg font-semibold text-white mb-1 truncate">
            {stream.name || stream.id}
          </h3>
          <p className="text-xs text-gray-500 font-mono truncate">ID: {stream.id}</p>
        </div>
        <span
          className={`px-3 py-1.5 text-xs font-medium rounded-full ring-1 flex items-center gap-1.5 flex-shrink-0 ml-2 ${config.color}`}
        >
          {config.icon}
          {stream.status || 'unknown'}
        </span>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 gap-4 mt-6 mb-4">
        <div className="bg-white/5 rounded-xl p-4 border border-white/5">
          <div className="text-xs text-gray-400 mb-2 uppercase tracking-wide">Count</div>
          <div className="text-3xl font-bold text-white">
            {stream.count ?? 0}
          </div>
        </div>
        <div className="bg-white/5 rounded-xl p-4 border border-white/5">
          <div className="text-xs text-gray-400 mb-2 uppercase tracking-wide">FPS</div>
          <div className="text-3xl font-bold text-white">
            {stream.fps ? stream.fps.toFixed(1) : '—'}
          </div>
        </div>
      </div>

      {/* Model Badge */}
      {stream.model && (
        <div className="mt-4 pt-4 border-t border-white/5">
          <div className="flex items-center justify-between">
            <span className="text-xs text-gray-400">Model</span>
            <span className="text-xs font-medium text-emerald-400 bg-emerald-500/10 px-2 py-1 rounded">
              {stream.model}
            </span>
          </div>
        </div>
      )}

      {/* Hover Effect Indicator */}
      <div className="absolute inset-0 rounded-2xl bg-gradient-to-r from-emerald-500/0 via-emerald-500/5 to-emerald-500/0 opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none"></div>
    </div>
  )
}
