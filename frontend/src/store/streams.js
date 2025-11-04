/** Zustand store for streams state */
import { create } from 'zustand'
import { streamsApi } from '../api/client'

const useStreamStore = create((set, get) => ({
  streams: [],
  loading: false,
  error: null,
  selectedStream: null,

  fetchStreams: async () => {
    set({ loading: true, error: null })
    try {
      const response = await streamsApi.list()
      set({ streams: response.data.streams || [], loading: false })
    } catch (error) {
      set({ error: error.message, loading: false })
    }
  },

  createStream: async (streamData) => {
    set({ loading: true, error: null })
    try {
      const response = await streamsApi.create(streamData)
      const newStream = response.data
      set((state) => ({
        streams: [...state.streams, newStream],
        loading: false,
      }))
      return newStream
    } catch (error) {
      set({ error: error.message, loading: false })
      throw error
    }
  },

  deleteStream: async (id) => {
    set({ loading: true, error: null })
    try {
      await streamsApi.delete(id)
      set((state) => ({
        streams: state.streams.filter((s) => s.id !== id),
        loading: false,
      }))
    } catch (error) {
      set({ error: error.message, loading: false })
      throw error
    }
  },

  selectStream: (stream) => {
    set({ selectedStream: stream })
  },
}))

export default useStreamStore

