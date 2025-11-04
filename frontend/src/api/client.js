/** API client for REST and WebSocket communication */
import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'
const WS_BASE = import.meta.env.VITE_WS_BASE || 'ws://localhost:8000'

// REST client
const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Streams API
export const streamsApi = {
  list: () => api.get('/streams'),
  create: (data) => api.post('/streams', data),
  get: (id) => api.get(`/streams/${id}/stats`),
  delete: (id) => api.delete(`/streams/${id}`),
}

// Inference API
export const inferenceApi = {
  infer: async (file) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post('/infer', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
  },
}

// WebSocket client helper
export const wsLive = (id, onMessage) => {
  const wsUrl = `${WS_BASE}/ws/streams/${id}/live`
  const ws = new WebSocket(wsUrl)

  ws.onopen = () => {
    console.log(`WebSocket connected for stream ${id}`)
  }

  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data)
      onMessage(data)
    } catch (error) {
      console.error('Error parsing WebSocket message:', error)
    }
  }

  ws.onerror = (error) => {
    console.error('WebSocket error:', error.message || 'Connection error')
  }

  ws.onclose = () => {
    console.log(`WebSocket closed for stream ${id}`)
  }

  return () => {
    if (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING) {
      ws.close()
    }
  }
}

// Legacy WebSocketClient class for backward compatibility
export class WebSocketClient {
  constructor(streamId) {
    this.streamId = streamId
    this.ws = null
    this.reconnectAttempts = 0
    this.maxReconnectAttempts = 5
    this.onMessage = null
    this.onError = null
    this.onClose = null
  }

  connect() {
    const wsUrl = `${WS_BASE}/ws/streams/${this.streamId}/live`
    this.ws = new WebSocket(wsUrl)

    this.ws.onopen = () => {
      console.log(`WebSocket connected for stream ${this.streamId}`)
      this.reconnectAttempts = 0
    }

    this.ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        if (this.onMessage) {
          this.onMessage(data)
        }
      } catch (error) {
        console.error('Error parsing WebSocket message:', error)
      }
    }

    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error.message || 'Connection error')
      if (this.onError) {
        this.onError(error)
      }
    }

    this.ws.onclose = () => {
      console.log(`WebSocket closed for stream ${this.streamId}`)
      if (this.onClose) {
        this.onClose()
      }
      this.reconnect()
    }
  }

  reconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++
      setTimeout(() => {
        console.log(`Reconnecting... (attempt ${this.reconnectAttempts})`)
        this.connect()
      }, 1000 * this.reconnectAttempts)
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
  }

  send(data) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data))
    }
  }
}

export default api
