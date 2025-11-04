/** Stream detail page with live updates */
import { useEffect, useState } from 'react'
import { useParams, useSearchParams, useNavigate } from 'react-router-dom'
import { wsLive } from '../api/client'
import HeatmapCanvas from '../components/HeatmapCanvas'
import StatsPanel from '../components/StatsPanel'
import ZonePanel from '../components/ZonePanel'
import TimelineChart from '../components/TimelineChart'
import AlertBanner from '../components/AlertBanner'
import ZoneEditor from '../components/ZoneEditor'

export default function StreamDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const [live, setLive] = useState(null)
  const [alpha, setAlpha] = useState(0.55)
  const [modelMode, setModelMode] = useState('hybrid')
  const [isPaused, setIsPaused] = useState(false)
  const [timeline, setTimeline] = useState([])

  const isZoneEdit = searchParams.get('edit') === 'zones'

  useEffect(() => {
    if (isPaused) return

    const cleanup = wsLive(id, (data) => {
      setLive(data)

      // Update timeline
      setTimeline((prev) => {
        const newTimeline = [...prev, { count: data.count, ts: data.ts || Date.now() }]
        // Keep last 60 points (5 minutes at ~5s intervals)
        return newTimeline.slice(-60)
      })
    })

    return cleanup
  }, [id, isPaused])

  const alerts = live?.zones?.filter((z) => z.alert) || []

  if (isZoneEdit) {
    return (
      <div className="max-w-7xl mx-auto space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="text-3xl font-bold text-white">Edit Zones: {id}</h1>
          <button
            onClick={() => navigate(`/streams/${id}`)}
            className="px-4 py-2 bg-white/5 text-gray-300 rounded-lg hover:bg-white/10 transition-colors"
          >
            Back to Stream
          </button>
        </div>
        <div className="bg-[#1C1C1C] border border-white/5 rounded-2xl p-6">
          <ZoneEditor
            imageSrc={live?.frame_url || live?.frame}
            zones={live?.zones || []}
            onSave={(zones) => {
              // TODO: Save zones to backend
              console.log('Saving zones:', zones)
              navigate(`/streams/${id}`)
            }}
            onCancel={() => navigate(`/streams/${id}`)}
          />
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">
            {live?.name || `Stream: ${id}`}
          </h1>
          <div className="flex items-center gap-3">
            <span
              className={`px-3 py-1 text-xs font-medium rounded-full ${
                live?.status === 'running'
                  ? 'bg-emerald-500/20 text-emerald-400 ring-1 ring-emerald-400/30'
                  : 'bg-gray-500/20 text-gray-400'
              }`}
            >
              {live?.status || 'unknown'}
            </span>
            {live?.model && (
              <span className="px-3 py-1 text-xs font-medium bg-blue-500/20 text-blue-400 rounded-full">
                {live.model}
              </span>
            )}
          </div>
        </div>

        <div className="flex items-center gap-3">
          {/* Model Selector */}
          <select
            value={modelMode}
            onChange={(e) => setModelMode(e.target.value)}
            className="px-3 py-2 bg-[#1C1C1C] border border-white/10 rounded-lg text-sm text-white focus:outline-none focus:ring-1 focus:ring-emerald-400/50"
          >
            <option value="hybrid">Auto</option>
            <option value="detector">Detector</option>
            <option value="density">Density</option>
          </select>

          {/* Pause Button */}
          <button
            onClick={() => setIsPaused(!isPaused)}
            className="px-4 py-2 bg-[#1C1C1C] border border-white/10 rounded-lg text-sm text-white hover:bg-white/5 transition-colors"
          >
            {isPaused ? '▶️ Resume' : '⏸️ Pause'}
          </button>
        </div>
      </div>

      {/* Alerts */}
      {alerts.length > 0 && <AlertBanner alerts={alerts} />}

      {/* Main Content Grid */}
      <div className="grid lg:grid-cols-3 gap-6">
        {/* Video + Heatmap (2/3 width) */}
        <div className="lg:col-span-2 space-y-4">
          <div className="bg-[#1C1C1C] border border-white/5 rounded-2xl p-4">
            <div className="flex items-center justify-between mb-3">
              <div className="text-sm text-gray-400">
                Model: <span className="font-medium text-emerald-400">{live?.model || '—'}</span>
              </div>
              <div className="flex items-center gap-3">
                <span className="text-xs text-gray-400">Heatmap Opacity</span>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.05"
                  value={alpha}
                  onChange={(e) => setAlpha(+e.target.value)}
                  className="w-24"
                />
                <span className="text-xs text-gray-400 w-8">{Math.round(alpha * 100)}%</span>
              </div>
            </div>
            {live ? (
              <HeatmapCanvas
                frameUrl={live.frame_url || live.frame}
                heatmapUrl={live.heatmap}
                alpha={alpha}
              />
            ) : (
              <div className="w-full h-64 bg-[#0E0F11] rounded-xl flex items-center justify-center text-gray-400">
                Waiting for stream data...
              </div>
            )}
          </div>

          {/* Timeline Chart */}
          <TimelineChart data={timeline} />
        </div>

        {/* Sidebar Stats (1/3 width) */}
        <div className="space-y-4">
          <StatsPanel stats={live} />
          <ZonePanel zones={live?.zones} />
        </div>
      </div>
    </div>
  )
}
