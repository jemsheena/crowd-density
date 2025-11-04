/** Stream creation form component */
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { streamsApi } from '../api/client'
import useStreamStore from '../store/streams'

export default function StreamCreateForm({ onClose }) {
  const navigate = useNavigate()
  const { createStream } = useStreamStore()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  
  const [formData, setFormData] = useState({
    name: '',
    sourceKind: 'rtsp',
    sourceUrl: '',
    deviceIndex: 0,
    inferenceMode: 'hybrid',
    zones: [],
  })

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError(null)

    try {
      const streamData = {
        name: formData.name,
        source: {
          kind: formData.sourceKind,
          url: formData.sourceKind !== 'webcam' ? formData.sourceUrl : null,
          device_index: formData.sourceKind === 'webcam' ? formData.deviceIndex : null,
        },
        inference: {
          mode: formData.inferenceMode,
          detector: {
            model: 'yolov8n',
            conf: 0.25,
            imgsz: 960,
          },
          density: {
            model: 'csrnet_v1',
            input_size: 768,
          },
        },
        zones: formData.zones,
        output: {
          heatmap: {
            colormap: 'JET',
            alpha: 0.55,
          },
        },
      }

      const stream = await createStream(streamData)
      navigate(`/streams/${stream.id}`)
    } catch (err) {
      setError(err.message || 'Failed to create stream')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-[#1C1C1C] border border-white/5 rounded-2xl p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-white">Create Stream</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white transition-colors"
          >
            ✕
          </button>
        </div>

        {error && (
          <div className="mb-4 p-3 bg-red-500/20 border border-red-400/30 text-red-300 rounded-lg text-sm">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Name */}
          <div>
            <label className="block text-sm text-gray-400 mb-2">Stream Name</label>
            <input
              type="text"
              required
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="w-full px-4 py-2 bg-[#0E0F11] border border-white/10 rounded-lg text-white focus:outline-none focus:ring-1 focus:ring-emerald-400/50"
              placeholder="e.g., Mall Entrance Cam"
            />
          </div>

          {/* Source Type */}
          <div>
            <label className="block text-sm text-gray-400 mb-2">Source Type</label>
            <select
              value={formData.sourceKind}
              onChange={(e) => setFormData({ ...formData, sourceKind: e.target.value })}
              className="w-full px-4 py-2 bg-[#0E0F11] border border-white/10 rounded-lg text-white focus:outline-none focus:ring-1 focus:ring-emerald-400/50"
            >
              <option value="rtsp">RTSP Stream</option>
              <option value="file">Video File</option>
              <option value="webcam">Webcam</option>
            </select>
          </div>

          {/* Source URL/Device */}
          {formData.sourceKind !== 'webcam' ? (
            <div>
              <label className="block text-sm text-gray-400 mb-2">
                {formData.sourceKind === 'rtsp' ? 'RTSP URL' : 'File Path'}
              </label>
              <input
                type="text"
                required
                value={formData.sourceUrl}
                onChange={(e) => setFormData({ ...formData, sourceUrl: e.target.value })}
                className="w-full px-4 py-2 bg-[#0E0F11] border border-white/10 rounded-lg text-white focus:outline-none focus:ring-1 focus:ring-emerald-400/50"
                placeholder={formData.sourceKind === 'rtsp' ? 'rtsp://...' : '/path/to/video.mp4'}
              />
            </div>
          ) : (
            <div>
              <label className="block text-sm text-gray-400 mb-2">Device Index</label>
              <input
                type="number"
                min="0"
                value={formData.deviceIndex}
                onChange={(e) => setFormData({ ...formData, deviceIndex: parseInt(e.target.value) })}
                className="w-full px-4 py-2 bg-[#0E0F11] border border-white/10 rounded-lg text-white focus:outline-none focus:ring-1 focus:ring-emerald-400/50"
              />
            </div>
          )}

          {/* Inference Mode */}
          <div>
            <label className="block text-sm text-gray-400 mb-2">Inference Mode</label>
            <select
              value={formData.inferenceMode}
              onChange={(e) => setFormData({ ...formData, inferenceMode: e.target.value })}
              className="w-full px-4 py-2 bg-[#0E0F11] border border-white/10 rounded-lg text-white focus:outline-none focus:ring-1 focus:ring-emerald-400/50"
            >
              <option value="hybrid">Auto (Hybrid)</option>
              <option value="detector">Detector (YOLO)</option>
              <option value="density">Density (CSRNet)</option>
            </select>
          </div>

          {/* Actions */}
          <div className="flex gap-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-2 bg-white/5 border border-white/10 rounded-lg text-white hover:bg-white/10 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="flex-1 px-4 py-2 bg-emerald-500 text-white rounded-lg hover:bg-emerald-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Creating...' : 'Create Stream'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

