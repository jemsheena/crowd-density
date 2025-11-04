/** Alerts page */
export default function Alerts() {
  // TODO: Fetch alerts from API
  const alerts = []

  return (
    <div className="max-w-7xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-2">Alerts</h1>
        <p className="text-gray-400">Threshold breaches and notifications</p>
      </div>

      {alerts.length === 0 ? (
        <div className="text-center py-16 bg-[#1C1C1C] border border-white/5 rounded-2xl">
          <div className="text-6xl mb-4">🚨</div>
          <p className="text-gray-400 text-lg">No alerts</p>
          <p className="text-gray-500 text-sm">All zones are within thresholds</p>
        </div>
      ) : (
        <div className="space-y-4">
          {alerts.map((alert) => (
            <div
              key={alert.id}
              className="bg-[#1C1C1C] border border-white/5 rounded-2xl p-6"
            >
              {/* Alert content */}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

