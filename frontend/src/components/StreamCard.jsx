/** Stream card component with live stats */
import { useNavigate } from 'react-router-dom'
import { useState } from 'react'

export default function StreamCard({ stream }) {
  const navigate = useNavigate()
  const [showActions, setShowActions] = useState(false)

  const statusColors = {
    running: 'bg-emerald-500/20 text-emerald-400 ring-emerald-400/30',
    starting: 'bg-yellow-500/20 text-yellow-400 ring-yellow-400/30',
    stopped: 'bg-gray-500/20 text-gray-400 ring-gray-400/30',
    error: 'bg-red-500/20 text-red-400 ring-red-400/30',
  }

  return (
    <div
      className="bg-[#1C1C1C] border border-white/5 rounded-2xl p-6 cursor-pointer hover:border-emerald-400/30 transition-all group relative"
      onMouseEnter={() => setShowActions(true)}
      onMouseLeave={() => setShowActions(false)}
      onClick={() => navigate(`/streams/${stream.id}`)}
    >
      {/* Quick Actions (on hover) */}
      {showActions && (
        <div className="absolute top-4 right-4 flex gap-2 z-10">
          <button
            onClick={(e) => {
              e.stopPropagation()
              navigate(`/streams/${stream.id}`)
            }}
            className="px-3 py-1.5 bg-emerald-500/20 text-emerald-400 text-xs rounded-lg hover:bg-emerald-500/30 transition-colors"
          >
            Open
          </button>
          <button
            onClick={(e) => {
              e.stopPropagation()
              navigate(`/streams/${stream.id}?edit=zones`)
            }}
            className="px-3 py-1.5 bg-blue-500/20 text-blue-400 text-xs rounded-lg hover:bg-blue-500/30 transition-colors"
          >
            Edit Zones
          </button>
        </div>
      )}

      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <h3 className="text-lg font-semibold text-white mb-1">
            {stream.name || stream.id}
          </h3>
          <p className="text-xs text-gray-400">ID: {stream.id}</p>
        </div>
        <span
          className={`px-2.5 py-1 text-xs font-medium rounded-full ring-1 ${
            statusColors[stream.status] || statusColors.stopped
          }`}
        >
          {stream.status}
        </span>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 gap-4 mt-4">
        <div>
          <div className="text-xs text-gray-400 mb-1">Count</div>
          <div className="text-2xl font-bold text-white">
            {stream.count ?? 0}
          </div>
        </div>
        <div>
          <div className="text-xs text-gray-400 mb-1">FPS</div>
          <div className="text-2xl font-bold text-white">
            {stream.fps ? stream.fps.toFixed(1) : '—'}
          </div>
        </div>
      </div>

      {/* Model Badge */}
      {stream.model && (
        <div className="mt-4 pt-4 border-t border-white/5">
          <span className="text-xs text-gray-400">Model: </span>
          <span className="text-xs font-medium text-emerald-400">
            {stream.model}
          </span>
        </div>
      )}
    </div>
  )
}
