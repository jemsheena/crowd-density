/** Stream creation form component */
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import useStreamStore from '../store/streams'

export default function StreamCreateForm({ onClose }) {
  const navigate = useNavigate()
  const { createStream, fetchStreams } = useStreamStore()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  
  const [formData, setFormData] = useState({
    name: '',
    sourceKind: 'file',
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
      await fetchStreams() // Refresh the list
      onClose()
      navigate(`/streams/${stream.id}`)
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Failed to create stream')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-50 p-4" onClick={onClose}>
      <div 
        className="bg-gradient-to-br from-[#1C1C1C] to-[#0E0F11] border border-white/10 rounded-2xl p-8 w-full max-w-2xl max-h-[90vh] overflow-y-auto shadow-2xl"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h2 className="text-3xl font-bold text-white mb-2">Create New Stream</h2>
            <p className="text-gray-400 text-sm">Configure your crowd density monitoring stream</p>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white transition-colors p-2 hover:bg-white/5 rounded-lg"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-6 p-4 bg-red-500/10 border border-red-500/30 rounded-xl text-red-300 flex items-start gap-3">
            <svg className="w-5 h-5 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <div className="flex-1">
              <p className="font-medium">Error</p>
              <p className="text-sm text-red-400/80 mt-1">{error}</p>
            </div>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Name */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Stream Name <span className="text-red-400">*</span>
            </label>
            <input
              type="text"
              required
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="w-full px-4 py-3 bg-[#0E0F11] border border-white/10 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500/50 transition-all"
              placeholder="e.g., Mall Entrance Camera"
            />
          </div>

          {/* Source Type */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Source Type <span className="text-red-400">*</span>
            </label>
            <div className="grid grid-cols-3 gap-3">
              {[
                { value: 'file', label: 'Video File', icon: '📹' },
                { value: 'rtsp', label: 'RTSP Camera', icon: '📡' },
                { value: 'webcam', label: 'Webcam', icon: '📷' },
              ].map((option) => (
                <button
                  key={option.value}
                  type="button"
                  onClick={() => setFormData({ ...formData, sourceKind: option.value })}
                  className={`px-4 py-3 rounded-xl border-2 transition-all ${
                    formData.sourceKind === option.value
                      ? 'border-emerald-500 bg-emerald-500/10 text-emerald-400'
                      : 'border-white/10 bg-[#0E0F11] text-gray-400 hover:border-white/20'
                  }`}
                >
                  <div className="text-2xl mb-1">{option.icon}</div>
                  <div className="text-sm font-medium">{option.label}</div>
                </button>
              ))}
            </div>
          </div>

          {/* Source URL/Device */}
          {formData.sourceKind !== 'webcam' ? (
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                {formData.sourceKind === 'rtsp' ? 'RTSP URL' : 'File Path'} <span className="text-red-400">*</span>
              </label>
              <input
                type="text"
                required
                value={formData.sourceUrl}
                onChange={(e) => setFormData({ ...formData, sourceUrl: e.target.value })}
                className="w-full px-4 py-3 bg-[#0E0F11] border border-white/10 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500/50 transition-all"
                placeholder={
                  formData.sourceKind === 'rtsp' 
                    ? 'rtsp://username:password@ip:port/stream' 
                    : 'C:\\Users\\USER\\Downloads\\video.mp4'
                }
              />
              {formData.sourceKind === 'file' && (
                <p className="mt-2 text-xs text-gray-500">
                  Use full Windows path (e.g., C:\Users\USER\Downloads\video.mp4)
                </p>
              )}
            </div>
          ) : (
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Device Index <span className="text-red-400">*</span>
              </label>
              <input
                type="number"
                min="0"
                value={formData.deviceIndex}
                onChange={(e) => setFormData({ ...formData, deviceIndex: parseInt(e.target.value) || 0 })}
                className="w-full px-4 py-3 bg-[#0E0F11] border border-white/10 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500/50 transition-all"
              />
              <p className="mt-2 text-xs text-gray-500">Usually 0 for the default webcam</p>
            </div>
          )}

          {/* Inference Mode */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Inference Mode
            </label>
            <select
              value={formData.inferenceMode}
              onChange={(e) => setFormData({ ...formData, inferenceMode: e.target.value })}
              className="w-full px-4 py-3 bg-[#0E0F11] border border-white/10 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500/50 transition-all"
            >
              <option value="hybrid">Auto (Hybrid) - Recommended</option>
              <option value="detector">Detector (YOLO) - For sparse crowds</option>
              <option value="density">Density (CSRNet) - For dense crowds</option>
            </select>
            <p className="mt-2 text-xs text-gray-500">
              Hybrid mode automatically selects the best model based on crowd density
            </p>
          </div>

          {/* Actions */}
          <div className="flex gap-3 pt-4 border-t border-white/10">
            <button
              type="button"
              onClick={onClose}
              disabled={loading}
              className="flex-1 px-6 py-3 bg-white/5 border border-white/10 rounded-xl text-white hover:bg-white/10 transition-colors disabled:opacity-50 disabled:cursor-not-allowed font-medium"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="flex-1 px-6 py-3 bg-gradient-to-r from-emerald-500 to-emerald-600 text-white rounded-xl hover:from-emerald-600 hover:to-emerald-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed font-medium shadow-lg shadow-emerald-500/20 flex items-center justify-center gap-2"
            >
              {loading ? (
                <>
                  <svg className="animate-spin h-5 w-5" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Creating...
                </>
              ) : (
                <>
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                  </svg>
                  Create Stream
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
