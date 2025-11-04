# Crowd Density Estimation System - Workflow Documentation

## 🧭 User-Level Workflow

### 1. Add a Stream
- Click "Create Stream" button on Dashboard
- Fill in form:
  - Stream name (e.g., "Mall Entrance Cam")
  - Source type (RTSP/File/Webcam)
  - Source URL or device index
  - Inference mode (Auto/Detector/Density)
- Click "Create Stream"
- Stream starts processing automatically

### 2. Watch Live
- Dashboard shows all streams with:
  - Live count
  - FPS
  - Status (running/starting/stopped/error)
  - Model badge
- Click on a stream card to open detail view
- See real-time video + heatmap overlay
- View per-zone counts and alerts

### 3. Edit Zones
- Open stream detail page
- Click "Edit Zones" button (or hover card → "Edit Zones")
- Draw polygons by clicking on video frame
- Set thresholds for each zone
- Save zones to backend

### 4. Monitor & Act
- View live counts updating in real-time
- See zone-specific counts with alert indicators
- Alerts appear when thresholds are exceeded
- Pause/resume stream processing
- Change model mode (Auto/Detector/Density)
- Adjust heatmap opacity

### 5. Review
- View alert history (future)
- Export snapshots/stats (future)
- Tweak model mode or thresholds
- View timeline chart of count history

---

## ⚙️ System Workflow (Data Flow)

```
[Camera/Video Source]
     │ frames
     ▼
[Ingestion Service]
  ├─ RTSP Reader
  ├─ File Reader
  └─ Webcam Reader
     │
     ▼
[Preprocessing]
  ├─ Resize/Normalize
  └─ Timestamp
     │
     ▼
[Hybrid Selector]
  ├─ Compute scene score (Laplacian variance)
  └─ Choose model (YOLO vs CSRNet)
     │
     ├─► [YOLO Detector] → boxes → box-density map
     └─► [CSRNet Density] → density map
                     │
                     ▼
[Post-processing]
  ├─ EMA smoothing
  ├─ Per-zone integration
  └─ Heatmap generation (PNG)
     │
     ▼
[State Management]
  ├─ Redis (stats cache)
  └─ Redis pub/sub (live updates)
     │
     ├─► [WebSocket to UI]
     └─► [Prometheus Metrics]
```

---

## 🧩 Backend Workflow

### Stream Creation (POST /streams)
1. Validate source configuration
2. Create stream config in memory store
3. Spawn `StreamWorker` background task
4. Initialize frame reader (RTSP/File/Webcam)
5. Load models (YOLO and/or CSRNet)
6. Initialize inference pipeline
7. Set status to "starting" → "running"
8. Start processing loop

### Frame Processing Loop
1. Read frame from source
2. Preprocess (resize, normalize)
3. Hybrid selector chooses model:
   - Compute Laplacian variance
   - If score > threshold_high → YOLO
   - If score < threshold_low → CSRNet
   - Use hysteresis to prevent flapping
4. Run inference:
   - YOLO: Detect people → count boxes → generate heatmap
   - CSRNet: Predict density map → sum for count
5. Post-process:
   - Apply EMA smoothing to counts
   - Integrate per-zone (mask overlap)
   - Generate heatmap PNG
   - Check alert thresholds
6. Update state:
   - Store stats in Redis
   - Publish to Redis pub/sub
   - Broadcast to WebSocket clients
7. Calculate FPS and latency
8. Repeat

### WebSocket Connection
1. Client connects to `/ws/streams/{id}/live`
2. Subscribe to Redis pub/sub channel
3. Send latest stats immediately
4. Forward all pub/sub messages to client
5. Handle disconnections gracefully

---

## 🖥️ Frontend Workflow

### Dashboard Load
1. `GET /streams` → fetch all streams
2. For each stream, get status from Redis
3. Render stream cards with live stats
4. Poll for updates (optional)

### Stream Detail
1. Connect WebSocket: `ws://localhost:8000/ws/streams/{id}/live`
2. Receive updates at 10-20 Hz:
   ```json
   {
     "type": "frame_stats",
     "ts": 1234567890.123,
     "count": 57,
     "zones": [...],
     "fps": 22.4,
     "model": "csrnet",
     "heatmap": "data:image/png;base64,..."
   }
   ```
3. Update UI:
   - Render heatmap overlay on canvas
   - Update count/FPS/latency displays
   - Update zone chips with alerts
   - Add to timeline chart
   - Show model badge

### Zone Editor
1. Load current frame from stream
2. Draw polygons by clicking
3. Edit vertices (drag to move, delete)
4. Set thresholds per zone
5. Save zones: `POST /zones` → update stream config

---

## 🔌 API Endpoints

- `POST /streams` - Create stream
- `GET /streams` - List all streams
- `GET /streams/{id}/stats` - Get current stats
- `DELETE /streams/{id}` - Stop and delete stream
- `WS /ws/streams/{id}/live` - Live WebSocket updates
- `POST /infer` - One-off image inference
- `POST /zones` - Save zones (future)
- `GET /alerts` - Alert history (future)

---

## 🧪 Operational Workflow

### Development
1. Start Redis: `docker run -d -p 6379:6379 redis:7-alpine`
2. Start backend: `uvicorn app.main:app --reload`
3. Start frontend: `npm run dev`
4. Open browser: `http://localhost:5173`

### Production
1. Use Docker Compose: `docker-compose -f deploy/docker-compose.dev.yml up`
2. Services start automatically:
   - API on port 8000
   - Redis on port 6379
   - Prometheus on port 9090
   - Grafana on port 3000
3. Mount model weights: `./models:/app/models`
4. Configure via `.env` file

---

## 🔄 Error Handling

### RTSP Connection Lost
- Reader retries with exponential backoff
- Status set to "degraded"
- UI shows "Reconnecting..." message
- Last known stats displayed

### Model Error
- Fallback to other model if available
- Emit `model="fallback"` flag
- Log error to Prometheus
- Continue processing next frame

### Slow Frame Rate
- Auto-drop frames if processing > 30 FPS
- Maintain latency budget
- Adjust FPS calculation

---

## ✅ Status

**Implemented:**
- ✅ Stream creation and worker spawning
- ✅ Redis state management
- ✅ WebSocket with Redis pub/sub
- ✅ Hybrid model selector
- ✅ YOLO detector integration
- ✅ CSRNet stub (ready for weights)
- ✅ EMA smoothing
- ✅ Zone integration
- ✅ Heatmap generation
- ✅ Alert threshold checking
- ✅ Frontend stream creation form
- ✅ Zone editor component
- ✅ Real-time WebSocket rendering

**Future Enhancements:**
- [ ] Full CSRNet model with weights
- [ ] Database persistence
- [ ] Alert history storage
- [ ] Zone save endpoint
- [ ] Export snapshots/stats
- [ ] Authentication
- [ ] Multi-user support

