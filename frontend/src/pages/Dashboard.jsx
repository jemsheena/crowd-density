/** Dashboard page with stream grid */
import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import useStreamStore from '../store/streams'
import StreamCard from '../components/StreamCard'
import StreamCreateForm from '../components/StreamCreateForm'

export default function Dashboard() {
  const navigate = useNavigate()
  const { streams, loading, error, fetchStreams } = useStreamStore()
  const [showCreateForm, setShowCreateForm] = useState(false)
  const [connectionStatus, setConnectionStatus] = useState('checking')

  useEffect(() => {
    fetchStreams()
    
    // Check API connection
    const checkConnection = async () => {
      try {
        const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'
        const response = await fetch(`${API_BASE}/health`)
        if (response.ok) {
          setConnectionStatus('connected')
        } else {
          setConnectionStatus('error')
        }
      } catch (err) {
        setConnectionStatus('error')
        console.error('API connection error:', err)
      }
    }
    
    checkConnection()
    
    // Auto-refresh every 5 seconds
    const interval = setInterval(() => {
      fetchStreams()
    }, 5000)
    
    return () => clearInterval(interval)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-4xl font-bold text-white mb-2">Crowd Density Monitoring</h1>
            <p className="text-gray-400">Monitor and analyze crowd density in real-time</p>
          </div>
          <button
            onClick={() => setShowCreateForm(true)}
            className="px-6 py-3 bg-gradient-to-r from-emerald-500 to-emerald-600 text-white rounded-xl hover:from-emerald-600 hover:to-emerald-700 transition-all shadow-lg shadow-emerald-500/20 font-medium flex items-center gap-2"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            Create Stream
          </button>
        </div>
        
        {/* Connection Status */}
        <div className="flex items-center gap-4 text-sm">
          <div className={`flex items-center gap-2 px-3 py-1.5 rounded-lg ${
            connectionStatus === 'connected' 
              ? 'bg-emerald-500/20 text-emerald-400' 
              : connectionStatus === 'error'
              ? 'bg-red-500/20 text-red-400'
              : 'bg-yellow-500/20 text-yellow-400'
          }`}>
            <div className={`w-2 h-2 rounded-full ${
              connectionStatus === 'connected' 
                ? 'bg-emerald-400 animate-pulse' 
                : connectionStatus === 'error'
                ? 'bg-red-400'
                : 'bg-yellow-400'
            }`}></div>
            {connectionStatus === 'connected' ? 'Connected' : connectionStatus === 'error' ? 'API Offline' : 'Checking...'}
          </div>
          {streams.length > 0 && (
            <span className="text-gray-400">
              {streams.length} {streams.length === 1 ? 'stream' : 'streams'} active
            </span>
          )}
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="mb-6 p-4 bg-red-500/10 border border-red-500/30 rounded-xl text-red-300 flex items-start gap-3">
          <svg className="w-5 h-5 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <div className="flex-1">
            <p className="font-medium">Connection Error</p>
            <p className="text-sm text-red-400/80 mt-1">{error}</p>
            <p className="text-xs text-red-400/60 mt-2">Make sure the backend is running on http://localhost:8000</p>
          </div>
          <button
            onClick={fetchStreams}
            className="px-3 py-1.5 bg-red-500/20 hover:bg-red-500/30 rounded-lg text-sm transition-colors"
          >
            Retry
          </button>
        </div>
      )}

      {/* Loading State */}
      {loading && !error && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1, 2, 3].map((i) => (
            <div
              key={i}
              className="bg-gradient-to-br from-[#1C1C1C] to-[#0E0F11] border border-white/5 rounded-2xl p-6 animate-pulse"
            >
              <div className="h-5 bg-white/10 rounded w-3/4 mb-4"></div>
              <div className="h-8 bg-white/10 rounded w-1/2 mb-6"></div>
              <div className="grid grid-cols-2 gap-4">
                <div className="h-16 bg-white/10 rounded"></div>
                <div className="h-16 bg-white/10 rounded"></div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Empty State */}
      {!loading && !error && streams.length === 0 && (
        <div className="text-center py-20 bg-gradient-to-br from-[#1C1C1C] to-[#0E0F11] border border-white/5 rounded-2xl">
          <div className="inline-flex items-center justify-center w-20 h-20 bg-emerald-500/10 rounded-full mb-6">
            <svg className="w-10 h-10 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
            </svg>
          </div>
          <h3 className="text-2xl font-bold text-white mb-2">No streams yet</h3>
          <p className="text-gray-400 mb-8 max-w-md mx-auto">
            Create your first stream to start monitoring crowd density. You can use video files, RTSP cameras, or webcams.
          </p>
          <button
            onClick={() => setShowCreateForm(true)}
            className="px-8 py-4 bg-gradient-to-r from-emerald-500 to-emerald-600 text-white rounded-xl hover:from-emerald-600 hover:to-emerald-700 transition-all shadow-lg shadow-emerald-500/20 font-medium inline-flex items-center gap-2"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            Create Your First Stream
          </button>
        </div>
      )}

      {/* Streams Grid */}
      {!loading && !error && streams.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {streams.map((stream) => (
            <StreamCard key={stream.id} stream={stream} />
          ))}
        </div>
      )}

      {/* Create Form Modal */}
      {showCreateForm && (
        <StreamCreateForm onClose={() => setShowCreateForm(false)} />
      )}
    </div>
  )
}
