/** Zone editor component with polygon drawing */
import { useState, useRef, useEffect } from 'react'

export default function ZoneEditor({ imageSrc, zones = [], onSave, onCancel }) {
  const canvasRef = useRef(null)
  const [currentZones, setCurrentZones] = useState(zones)
  const [isDrawing, setIsDrawing] = useState(false)
  const [currentPolygon, setCurrentPolygon] = useState([])
  const [selectedZone, setSelectedZone] = useState(null)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext('2d')

    // Load base image
    const img = new Image()
    img.crossOrigin = 'anonymous'
    img.onload = () => {
      canvas.width = img.width
      canvas.height = img.height
      ctx.drawImage(img, 0, 0)

      // Draw existing zones
      currentZones.forEach((zone, idx) => {
        drawZone(ctx, zone.polygon, zone.name || zone.id, idx === selectedZone)
      })

      // Draw current polygon being drawn
      if (currentPolygon.length > 0) {
        drawPolygon(ctx, currentPolygon)
      }
    }
    img.src = imageSrc || ''
  }, [imageSrc, currentZones, currentPolygon, selectedZone])

  const drawZone = (ctx, polygon, name, isSelected) => {
    if (!polygon || polygon.length < 3) return

    ctx.beginPath()
    ctx.moveTo(polygon[0][0], polygon[0][1])
    for (let i = 1; i < polygon.length; i++) {
      ctx.lineTo(polygon[i][0], polygon[i][1])
    }
    ctx.closePath()

    // Fill
    ctx.fillStyle = isSelected
      ? 'rgba(59, 130, 246, 0.4)'
      : 'rgba(16, 185, 129, 0.3)'
    ctx.fill()

    // Stroke
    ctx.strokeStyle = isSelected ? 'rgba(59, 130, 246, 1)' : 'rgba(16, 185, 129, 1)'
    ctx.lineWidth = isSelected ? 3 : 2
    ctx.stroke()

    // Draw vertices
    polygon.forEach((point, i) => {
      ctx.beginPath()
      ctx.arc(point[0], point[1], 5, 0, Math.PI * 2)
      ctx.fillStyle = isSelected ? '#3b82f6' : '#10b981'
      ctx.fill()
    })

    // Draw label
    if (name) {
      const centerX = polygon.reduce((sum, p) => sum + p[0], 0) / polygon.length
      const centerY = polygon.reduce((sum, p) => sum + p[1], 0) / polygon.length
      ctx.fillStyle = 'white'
      ctx.font = '14px Arial'
      ctx.textAlign = 'center'
      ctx.fillText(name, centerX, centerY)
    }
  }

  const drawPolygon = (ctx, polygon) => {
    if (polygon.length < 2) return

    ctx.beginPath()
    ctx.moveTo(polygon[0][0], polygon[0][1])
    for (let i = 1; i < polygon.length; i++) {
      ctx.lineTo(polygon[i][0], polygon[i][1])
    }
    if (polygon.length >= 3) {
      ctx.closePath()
    }

    ctx.strokeStyle = 'rgba(16, 185, 129, 1)'
    ctx.lineWidth = 2
    ctx.setLineDash([5, 5])
    ctx.stroke()
    ctx.setLineDash([])

    // Draw vertices
    polygon.forEach((point) => {
      ctx.beginPath()
      ctx.arc(point[0], point[1], 5, 0, Math.PI * 2)
      ctx.fillStyle = '#10b981'
      ctx.fill()
    })
  }

  const handleMouseDown = (e) => {
    if (!isDrawing) return

    const canvas = canvasRef.current
    const rect = canvas.getBoundingClientRect()
    const x = e.clientX - rect.left
    const y = e.clientY - rect.top

    setCurrentPolygon([...currentPolygon, [x, y]])
  }

  const handleSaveCurrentZone = () => {
    if (currentPolygon.length >= 3) {
      const newZone = {
        id: `zone_${Date.now()}`,
        name: `Zone ${currentZones.length + 1}`,
        polygon: currentPolygon,
        threshold: 50,
      }
      const updatedZones = [...currentZones, newZone]
      setCurrentZones(updatedZones)
      setCurrentPolygon([])
    }
  }

  const handleFinalSave = () => {
    if (onSave) {
      onSave(currentZones)
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-white">Zone Editor</h3>
        <div className="flex gap-2">
          <button
            onClick={() => setIsDrawing(!isDrawing)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              isDrawing
                ? 'bg-emerald-500 text-white'
                : 'bg-white/5 text-gray-300 hover:bg-white/10'
            }`}
          >
            {isDrawing ? 'Drawing...' : 'Draw Zone'}
          </button>
          {isDrawing && (
            <button
              onClick={handleSaveCurrentZone}
              disabled={currentPolygon.length < 3}
              className="px-4 py-2 bg-blue-500 text-white rounded-lg text-sm font-medium hover:bg-blue-600 transition-colors disabled:opacity-50"
            >
              Save Zone
            </button>
          )}
        </div>
      </div>

      <canvas
        ref={canvasRef}
        className="w-full border border-white/10 rounded-xl cursor-crosshair"
        onMouseDown={handleMouseDown}
      />

      <div className="flex gap-2">
        <button
          onClick={() => setCurrentPolygon([])}
          className="px-4 py-2 bg-white/5 text-gray-300 rounded-lg text-sm hover:bg-white/10 transition-colors"
        >
          Clear Current
        </button>
        <button
          onClick={handleFinalSave}
          className="px-4 py-2 bg-emerald-500 text-white rounded-lg text-sm font-medium hover:bg-emerald-600 transition-colors"
        >
          Save All Zones
        </button>
        {onCancel && (
          <button
            onClick={onCancel}
            className="px-4 py-2 bg-white/5 text-gray-300 rounded-lg text-sm hover:bg-white/10 transition-colors"
          >
            Cancel
          </button>
        )}
      </div>

      {currentZones.length > 0 && (
        <div className="mt-4">
          <h4 className="text-sm font-medium text-white mb-2">Zones ({currentZones.length})</h4>
          <div className="space-y-2">
            {currentZones.map((zone, idx) => (
              <div
                key={zone.id}
                onClick={() => setSelectedZone(idx === selectedZone ? null : idx)}
                className={`p-2 rounded-lg cursor-pointer transition-colors ${
                  idx === selectedZone ? 'bg-blue-500/20 border border-blue-400/30' : 'bg-white/5 hover:bg-white/10'
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="text-sm text-white">{zone.name || zone.id}</span>
                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      setCurrentZones(currentZones.filter((_, i) => i !== idx))
                    }}
                    className="text-red-400 hover:text-red-300 text-sm"
                  >
                    Delete
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
