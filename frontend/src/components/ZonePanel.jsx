/** Zone panel showing per-zone counts and alerts */
export default function ZonePanel({ zones = [] }) {
  if (!zones || zones.length === 0) {
    return (
      <div className="bg-[#1C1C1C] border border-white/5 rounded-2xl p-4">
        <div className="text-sm font-medium text-white mb-2">Zones</div>
        <div className="text-xs text-gray-400">No zones configured</div>
      </div>
    )
  }

  return (
    <div className="bg-[#1C1C1C] border border-white/5 rounded-2xl p-4">
      <div className="text-sm font-medium text-white mb-3">Zones</div>
      <div className="space-y-2">
        {zones.map((zone) => (
          <div
            key={zone.id}
            className="flex items-center justify-between p-2 rounded-lg bg-white/5 hover:bg-white/10 transition-colors"
          >
            <div className="flex-1 min-w-0">
              <div className="text-sm font-medium text-white truncate">
                {zone.id}
              </div>
              {zone.name && (
                <div className="text-xs text-gray-400 truncate">{zone.name}</div>
              )}
            </div>
            <div className="flex items-center gap-2">
              <span
                className={`px-2.5 py-1 rounded-full text-xs font-medium ${
                  zone.alert
                    ? 'bg-red-500/20 text-red-300 ring-1 ring-red-400/30'
                    : 'bg-emerald-500/20 text-emerald-300 ring-1 ring-emerald-400/30'
                }`}
              >
                {zone.count ?? 0}
              </span>
              {zone.threshold && (
                <span className="text-xs text-gray-500">
                  / {zone.threshold}
                </span>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

