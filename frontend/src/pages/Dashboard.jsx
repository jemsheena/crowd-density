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

  useEffect(() => {
    fetchStreams()
  }, [])

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1, 2, 3].map((i) => (
            <div
              key={i}
              className="bg-[#1C1C1C] border border-white/5 rounded-2xl p-6 animate-pulse"
            >
              <div className="h-4 bg-white/10 rounded w-3/4 mb-4"></div>
              <div className="h-8 bg-white/10 rounded w-1/2"></div>
            </div>
          ))}
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="max-w-7xl mx-auto">
        <div className="bg-red-500/20 border border-red-400/30 text-red-300 px-4 py-3 rounded-lg">
          Error: {error}
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-7xl mx-auto">
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">Streams</h1>
          <p className="text-gray-400">Manage your crowd density monitoring streams</p>
        </div>
        <button
          onClick={() => setShowCreateForm(true)}
          className="px-4 py-2 bg-emerald-500 text-white rounded-lg hover:bg-emerald-600 transition-colors font-medium"
        >
          + Create Stream
        </button>
      </div>

      {streams.length === 0 ? (
        <div className="text-center py-16 bg-[#1C1C1C] border border-white/5 rounded-2xl">
          <div className="text-6xl mb-4">📹</div>
          <p className="text-gray-400 text-lg mb-2">No streams yet</p>
          <p className="text-gray-500 text-sm mb-6">Create one to get started</p>
          <button
            onClick={() => setShowCreateForm(true)}
            className="px-6 py-3 bg-emerald-500 text-white rounded-lg hover:bg-emerald-600 transition-colors font-medium"
          >
            Create Stream
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {streams.map((stream) => (
            <StreamCard key={stream.id} stream={stream} />
          ))}
        </div>
      )}

      {showCreateForm && (
        <StreamCreateForm onClose={() => setShowCreateForm(false)} />
      )}
    </div>
  )
}
