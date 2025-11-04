# Crowd Density Estimation System - User Guide

## 🚀 Quick Start

### Step 1: Start the System

**Terminal 1 - Backend:**
```powershell
cd backend
uvicorn app.main:app --reload
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Terminal 2 - Frontend:**
```powershell
cd frontend
npm run dev
```

You should see:
```
VITE v5.4.21  ready in 616 ms
➜  Local:   http://localhost:5173/
```

**Optional - Redis (for full functionality):**
```powershell
docker run -d -p 6379:6379 redis:7-alpine
```

---

## 🎯 Using the System

### 1. Access the Dashboard

1. Open your browser: `http://localhost:5173`
2. You'll see the **Dashboard** with the sidebar navigation

### 2. Create Your First Stream

**On the Dashboard:**
1. Click the **"+ Create Stream"** button (top right)
2. Fill in the form:
   - **Stream Name**: e.g., "Mall Entrance Cam"
   - **Source Type**: Choose one:
     - **RTSP Stream**: For IP cameras
     - **Video File**: For local video files
     - **Webcam**: For your computer's camera
   - **Source URL/Path**: 
     - RTSP: `rtsp://username:password@camera-ip:554/stream`
     - File: `C:\path\to\video.mp4` or `/path/to/video.mp4`
     - Webcam: Device index (usually `0`)
   - **Inference Mode**:
     - **Auto (Hybrid)**: Automatically chooses best model
     - **Detector (YOLO)**: Best for sparse crowds
     - **Density (CSRNet)**: Best for dense crowds
3. Click **"Create Stream"**

### 3. View Live Stream

**After creating a stream:**
1. You'll be redirected to the **Stream Detail** page
2. You'll see:
   - **Video + Heatmap**: Live video with density overlay
   - **Stats Panel**: Total count, FPS, latency, model
   - **Zone Panel**: Per-zone counts and alerts
   - **Timeline Chart**: Count history over time

**Or from Dashboard:**
1. Click on any **Stream Card** to view details
2. Hover over cards to see quick actions:
   - **Open**: View stream detail
   - **Edit Zones**: Draw monitoring zones

### 4. Edit Zones (Optional)

**On Stream Detail Page:**
1. Click **"Edit Zones"** button (or hover card → "Edit Zones")
2. In the Zone Editor:
   - Click **"Draw Zone"** button to enable drawing
   - Click on the video frame to draw polygon vertices
   - Click at least 3 points to form a zone
   - Click **"Save Zone"** to add the zone
   - Repeat for multiple zones
3. Set thresholds for each zone (optional)
4. Click **"Save All Zones"** when done

**Zone Features:**
- Each zone can have a threshold
- When count exceeds threshold, alert is triggered
- Zones are displayed with colored borders
- Counts are shown per zone

### 5. Monitor Live Data

**On Stream Detail Page:**

**Controls:**
- **Model Selector**: Switch between Auto/Detector/Density
- **Heatmap Opacity Slider**: Adjust heatmap visibility (0-100%)
- **Pause/Resume**: Pause stream processing

**Stats Display:**
- **Total Count**: Current number of people detected
- **FPS**: Processing frames per second
- **Latency**: Processing time per frame
- **Model Badge**: Shows which model is active (YOLO/CSRNet)

**Zones:**
- Each zone shows its count
- Green = below threshold
- Red = above threshold (alert)

**Timeline:**
- Shows count history over last few minutes
- Updates in real-time

### 6. Navigate the Interface

**Left Sidebar:**
- **📹 Streams**: Main dashboard (default)
- **🚨 Alerts**: View all active alerts
- **📊 History**: Historical data (coming soon)
- **⚙️ Settings**: System configuration

**Top Bar:**
- **Search**: Search streams by name
- **User**: User menu (coming soon)

---

## 📹 Stream Types

### RTSP Stream
- **Format**: `rtsp://username:password@ip:port/stream`
- **Example**: `rtsp://admin:password123@192.168.1.100:554/stream1`
- **Use Case**: IP cameras, CCTV systems

### Video File
- **Format**: Full path to video file
- **Example**: `C:\Videos\crowd.mp4` or `/home/user/video.mp4`
- **Use Case**: Pre-recorded videos, testing

### Webcam
- **Format**: Device index (usually 0, 1, 2...)
- **Example**: `0` for first webcam
- **Use Case**: Live webcam feed, testing

---

## 🎛️ Inference Modes

### Auto (Hybrid) - Recommended
- Automatically chooses best model based on scene
- Uses **YOLO** for sparse crowds (detects individuals)
- Uses **CSRNet** for dense crowds (estimates density)
- Seamlessly switches between models

### Detector (YOLO)
- Best for: Sparse to medium density
- Provides: Individual person detection
- Shows: Bounding boxes (converted to heatmap)

### Density (CSRNet)
- Best for: High density crowds
- Provides: Density map estimation
- Shows: Continuous density heatmap

---

## 🚨 Alerts

**Alert Triggers:**
- Zone count exceeds threshold
- Alert appears in red banner
- Alert shown in zone panel with red chip

**Viewing Alerts:**
1. Click **"Alerts"** in sidebar
2. See all active alerts across streams
3. Filter by stream or time

---

## ⚙️ Settings

**Model Settings:**
- Default inference mode
- Model parameters
- Thresholds

**Display Settings:**
- Default heatmap opacity
- Colormap selection
- Update frequency

---

## 🔧 Troubleshooting

### Stream Not Starting
- Check source URL/path is correct
- Verify RTSP credentials
- Ensure video file exists and is readable
- Check webcam is connected (if using webcam)

### No Live Updates
- Check Redis is running (if using)
- Verify WebSocket connection in browser console
- Check backend logs for errors
- Ensure stream status is "running"

### No Counts Showing
- Stream may be processing (wait a few seconds)
- Check if model weights are loaded
- Verify video source has people visible
- Check backend logs for errors

### Heatmap Not Showing
- Adjust opacity slider
- Check if density map is being generated
- Verify WebSocket is receiving heatmap data

---

## 💡 Tips

1. **Start with a test video** before using live RTSP
2. **Use Auto mode** for best results
3. **Draw zones** to monitor specific areas
4. **Set thresholds** based on expected crowd size
5. **Monitor FPS** - if too low, reduce video resolution
6. **Check model badge** to see which model is active

---

## 📊 Understanding the Display

**Color Legend:**
- **Blue/Green**: Low density
- **Yellow**: Medium density  
- **Red**: High density

**Zone Colors:**
- **Green chip**: Normal (below threshold)
- **Red chip**: Alert (above threshold)

**Model Badge:**
- Shows current active model
- **YOLOv8**: Detector mode
- **CSRNet**: Density mode
- **Auto**: Hybrid mode

---

## 🎬 Example Workflow

1. **Create Stream** with RTSP URL
2. **Wait for processing** to start (status → "running")
3. **View live stream** with heatmap overlay
4. **Draw zones** around areas of interest (entrance, exit, stage)
5. **Set thresholds** for each zone (e.g., 50 people)
6. **Monitor counts** in real-time
7. **Receive alerts** when thresholds exceeded
8. **Review timeline** to see crowd patterns

---

## 🔗 API Endpoints

You can also use the API directly:

- **API Docs**: `http://localhost:8000/docs`
- **Health Check**: `http://localhost:8000/health`
- **Streams List**: `GET http://localhost:8000/streams`
- **Create Stream**: `POST http://localhost:8000/streams`
- **Stream Stats**: `GET http://localhost:8000/streams/{id}/stats`

---

## 📝 Next Steps

1. **Create your first stream** with a test video
2. **Explore the UI** and all features
3. **Draw zones** to monitor specific areas
4. **Set up alerts** for crowd management
5. **Connect to real cameras** for production use

---

For more details, see:
- `SETUP_OPTIONS.md` - Setup instructions
- `WORKFLOW.md` - Technical workflow
- `README.md` - System overview

