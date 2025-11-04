# Quick Start Guide - Video Sources

## 🎥 Video Source Options

You have **3 ways** to provide video input:

---

## Option 1: RTSP Stream (IP Camera) 📹

**Best for:** Live IP cameras, CCTV systems, security cameras

**How to use:**
1. Click "+ Create Stream"
2. Select **"RTSP Stream"** as source type
3. Enter RTSP URL:
   ```
   rtsp://username:password@camera-ip:port/stream
   ```

**Example URLs:**
```
rtsp://admin:password123@192.168.1.100:554/stream1
rtsp://user:pass@10.0.0.50:8554/live
rtsp://192.168.1.64:554/Streaming/Channels/101
```

**Common RTSP ports:**
- 554 (default)
- 8554 (alternative)

**Finding your camera RTSP URL:**
- Check camera documentation
- Look in camera settings/web interface
- Common formats:
  - `/stream1` or `/stream2`
  - `/live` or `/live.sdp`
  - `/Streaming/Channels/101`

---

## Option 2: Video File 📁

**Best for:** Testing, pre-recorded videos, analysis of past events

**How to use:**
1. Click "+ Create Stream"
2. Select **"Video File"** as source type
3. Enter full path to video file:
   ```
   C:\Videos\crowd_video.mp4
   ```
   or
   ```
   /home/user/videos/crowd.mp4
   ```

**Supported formats:**
- `.mp4` (recommended)
- `.avi`
- `.mov`
- `.mkv`
- Most formats supported by OpenCV

**Example paths:**
```
Windows:  C:\Users\USER\Videos\crowd.mp4
Windows:  D:\Recordings\mall_entrance.mp4
Linux/Mac: /home/user/videos/test.mp4
```

**Tip:** Use a video file for testing before connecting to live cameras!

---

## Option 3: Webcam 🖥️

**Best for:** Testing, live webcam feed, development

**How to use:**
1. Click "+ Create Stream"
2. Select **"Webcam"** as source type
3. Enter device index:
   - `0` = First webcam
   - `1` = Second webcam
   - `2` = Third webcam, etc.

**Finding your webcam index:**
- Usually `0` for built-in webcam
- `1` for first USB webcam
- Try different numbers if unsure

**Example:**
- Built-in laptop camera: `0`
- USB webcam: `1`

---

## 🎯 Recommended Testing Flow

### Step 1: Test with Video File (Easiest)
1. Find any video file on your computer
2. Create stream with "Video File" source
3. Enter full path: `C:\path\to\your\video.mp4`
4. Test the system works

### Step 2: Test with Webcam (If available)
1. Create stream with "Webcam" source
2. Use device index `0`
3. Point webcam at scene with people
4. See real-time detection

### Step 3: Use RTSP Camera (Production)
1. Get camera RTSP URL from camera settings
2. Create stream with "RTSP Stream" source
3. Enter RTSP URL
4. Monitor live feed

---

## 📝 Example: Testing with Video File

**Step-by-step:**

1. **Find or create a test video:**
   - Any video with people in it
   - Or download a sample from internet
   - Place it in an easy location like `C:\Videos\test.mp4`

2. **Create stream:**
   - Open dashboard: `http://localhost:5173`
   - Click "+ Create Stream"
   - Name: "Test Video"
   - Source Type: **Video File**
   - Source URL: `C:\Videos\test.mp4`
   - Inference Mode: **Auto**
   - Click "Create Stream"

3. **Watch it process:**
   - Stream starts automatically
   - Video plays with heatmap overlay
   - Counts update in real-time
   - Stats show FPS and latency

---

## 💡 Tips

### For Testing:
- ✅ Start with a **video file** (easiest)
- ✅ Use short videos (1-2 minutes) for quick testing
- ✅ Make sure video has people visible

### For Production:
- ✅ Use **RTSP streams** from IP cameras
- ✅ Set up zones for specific areas
- ✅ Configure alerts with thresholds

### Troubleshooting:
- **File not found**: Check path is correct (use full path)
- **RTSP not connecting**: Verify URL, credentials, network
- **Webcam not working**: Try different device index (0, 1, 2...)
- **No video showing**: Check if source is valid and accessible

---

## 🔍 Finding Your Video Source

### RTSP Camera:
1. Check camera brand documentation
2. Common RTSP formats:
   - Hikvision: `rtsp://admin:password@ip:554/Streaming/Channels/101`
   - Dahua: `rtsp://admin:password@ip:554/cam/realmonitor?channel=1`
   - Generic: `rtsp://ip:554/stream1`

### Video File:
- Use Windows Explorer to find file path
- Right-click file → Properties → Copy path
- Or drag file into browser to get path

### Webcam:
- Usually device `0` for built-in camera
- Try `0`, `1`, `2` until one works
- Check Device Manager to see available cameras

---

## ✅ You DON'T Need:

- ❌ No need to upload video to server
- ❌ No need to convert video format (most formats work)
- ❌ No need for special video encoding
- ❌ No need to host video files

**Just provide the path or URL!** The system reads it directly.

---

## 🎬 Quick Test Right Now

**If you have a video file:**
1. Note the full path (e.g., `C:\Users\USER\Downloads\video.mp4`)
2. Create stream with that path
3. Watch it process!

**If you have a webcam:**
1. Create stream with device index `0`
2. Point camera at scene
3. See real-time detection!

**If you have an IP camera:**
1. Get RTSP URL from camera settings
2. Create stream with that URL
3. Monitor live feed!

---

The system reads video directly from the source - no need to upload or convert anything!

