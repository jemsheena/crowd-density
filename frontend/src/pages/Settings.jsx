/** Settings page */
export default function Settings() {
  return (
    <div className="max-w-7xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-2">Settings</h1>
        <p className="text-gray-400">Configure models, thresholds, and preferences</p>
      </div>

      <div className="bg-[#1C1C1C] border border-white/5 rounded-2xl p-6 space-y-6">
        <div>
          <h2 className="text-lg font-semibold text-white mb-4">Model Settings</h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm text-gray-400 mb-2">Default Mode</label>
              <select className="w-full px-4 py-2 bg-[#0E0F11] border border-white/10 rounded-lg text-white focus:outline-none focus:ring-1 focus:ring-emerald-400/50">
                <option>Hybrid</option>
                <option>Detector</option>
                <option>Density</option>
              </select>
            </div>
          </div>
        </div>

        <div>
          <h2 className="text-lg font-semibold text-white mb-4">Display Settings</h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm text-gray-400 mb-2">Default Heatmap Opacity</label>
              <input
                type="range"
                min="0"
                max="1"
                step="0.05"
                defaultValue="0.55"
                className="w-full"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
