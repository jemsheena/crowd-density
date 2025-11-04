/** Heatmap canvas with alpha-blend overlay */
import { useEffect, useRef } from 'react'

export default function HeatmapCanvas({ frameUrl, heatmapUrl, alpha = 0.55 }) {
  const canvasRef = useRef(null)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext('2d')
    const bg = new Image()
    const hm = new Image()
    let mounted = true

    const draw = () => {
      if (!mounted) return

      canvas.width = bg.naturalWidth || 1920
      canvas.height = bg.naturalHeight || 1080

      // Draw base frame
      ctx.drawImage(bg, 0, 0, canvas.width, canvas.height)

      // Draw heatmap overlay if provided
      if (heatmapUrl && hm.complete) {
        ctx.globalAlpha = alpha
        ctx.drawImage(hm, 0, 0, canvas.width, canvas.height)
        ctx.globalAlpha = 1.0
      }
    }

    bg.crossOrigin = 'anonymous'
    bg.onload = () => {
      if (heatmapUrl) {
        hm.crossOrigin = 'anonymous'
        hm.onload = draw
        hm.src = heatmapUrl
      } else {
        draw()
      }
    }
    bg.onerror = () => {
      // If frame fails, draw placeholder
      if (mounted) {
        ctx.fillStyle = '#1C1C1C'
        ctx.fillRect(0, 0, canvas.width || 1920, canvas.height || 1080)
        ctx.fillStyle = '#666'
        ctx.font = '24px Arial'
        ctx.textAlign = 'center'
        ctx.fillText('No frame available', canvas.width / 2, canvas.height / 2)
      }
    }

    bg.src = frameUrl || ''

    return () => {
      mounted = false
    }
  }, [frameUrl, heatmapUrl, alpha])

  return (
    <canvas
      ref={canvasRef}
      className="w-full h-auto rounded-xl"
      style={{ maxWidth: '100%' }}
    />
  )
}
