/** Simple timeline chart for count history */
import { useEffect, useRef } from 'react'

export default function TimelineChart({ data = [], height = 120 }) {
  const canvasRef = useRef(null)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas || !data || data.length === 0) return

    const ctx = canvas.getContext('2d')
    const width = canvas.width
    const h = canvas.height

    // Clear canvas
    ctx.clearRect(0, 0, width, h)

    // Draw grid
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.05)'
    ctx.lineWidth = 1
    for (let i = 0; i <= 5; i++) {
      const y = (h / 5) * i
      ctx.beginPath()
      ctx.moveTo(0, y)
      ctx.lineTo(width, y)
      ctx.stroke()
    }

    // Draw line
    const maxCount = Math.max(...data.map((d) => d.count), 1)
    const padding = 20

    ctx.strokeStyle = '#10b981'
    ctx.lineWidth = 2
    ctx.beginPath()

    data.forEach((point, i) => {
      const x = (width / (data.length - 1 || 1)) * i
      const y = h - (point.count / maxCount) * (h - padding * 2) - padding

      if (i === 0) {
        ctx.moveTo(x, y)
      } else {
        ctx.lineTo(x, y)
      }
    })

    ctx.stroke()

    // Draw points
    ctx.fillStyle = '#10b981'
    data.forEach((point, i) => {
      const x = (width / (data.length - 1 || 1)) * i
      const y = h - (point.count / maxCount) * (h - padding * 2) - padding

      ctx.beginPath()
      ctx.arc(x, y, 3, 0, Math.PI * 2)
      ctx.fill()
    })
  }, [data, height])

  return (
    <div className="bg-[#1C1C1C] border border-white/5 rounded-2xl p-4">
      <div className="text-sm font-medium text-white mb-3">Timeline</div>
      <canvas
        ref={canvasRef}
        width={600}
        height={height}
        className="w-full h-auto"
      />
      {(!data || data.length === 0) && (
        <div className="text-xs text-gray-400 text-center py-4">
          No data available
        </div>
      )}
    </div>
  )
}

