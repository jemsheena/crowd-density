/** Stats panel showing count, FPS, latency, model */
export default function StatsPanel({ stats }) {
  return (
    <div className="bg-[#1C1C1C] border border-white/5 rounded-2xl p-4 space-y-4">
      <div>
        <div className="text-xs text-gray-400 mb-1">Total Count</div>
        <div className="text-3xl font-bold text-white">
          {Math.round(stats?.count ?? 0)}
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4 pt-4 border-t border-white/5">
        <div>
          <div className="text-xs text-gray-400 mb-1">FPS</div>
          <div className="text-lg font-semibold text-white">
            {stats?.fps ? stats.fps.toFixed(1) : '—'}
          </div>
        </div>
        <div>
          <div className="text-xs text-gray-400 mb-1">Latency</div>
          <div className="text-lg font-semibold text-white">
            {stats?.latency_ms ? `${stats.latency_ms.toFixed(0)} ms` : '—'}
          </div>
        </div>
      </div>

      {stats?.model && (
        <div className="pt-4 border-t border-white/5">
          <div className="text-xs text-gray-400 mb-1">Model</div>
          <div className="inline-flex items-center gap-2 px-3 py-1.5 bg-emerald-500/20 text-emerald-400 rounded-lg text-sm font-medium">
            <span className="w-2 h-2 bg-emerald-400 rounded-full animate-pulse"></span>
            {stats.model}
          </div>
        </div>
      )}
    </div>
  )
}

