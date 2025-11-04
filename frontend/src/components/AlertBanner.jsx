/** Alert banner component */
export default function AlertBanner({ alerts = [] }) {
  if (!alerts || alerts.length === 0) return null

  return (
    <div className="mb-6 space-y-2">
      {alerts.map((alert) => (
        <div
          key={alert.id}
          className="bg-red-500/20 border border-red-400/30 text-red-300 px-4 py-3 rounded-lg flex items-center justify-between"
        >
          <div className="flex items-center gap-3">
            <span className="text-xl">🚨</span>
            <div>
              <div className="font-medium">Alert: {alert.zone}</div>
              <div className="text-sm text-red-200">
                Count: {alert.count} (Threshold: {alert.threshold})
              </div>
            </div>
          </div>
          <button className="text-red-300 hover:text-red-200 text-sm">
            Dismiss
          </button>
        </div>
      ))}
    </div>
  )
}
