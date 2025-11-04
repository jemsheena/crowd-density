# Logging Configuration

## Overview

The Crowd Density system now includes comprehensive logging throughout all components. Logs are written to both console and files for easy debugging and error tracking.

## Log Files

Logs are written to `backend/logs/crowd-density-YYYYMMDD.log` with rotation:
- Max file size: 10MB per file
- Backup count: 5 files
- Format: `YYYY-MM-DD HH:MM:SS - logger_name - LEVEL - file:line - message`

## Log Levels

- **DEBUG**: Detailed information for debugging (frame counts, message counts, etc.)
- **INFO**: General informational messages (startup, connections, stream creation)
- **WARNING**: Warnings about non-critical issues (Redis unavailable, fallback mode)
- **ERROR**: Error messages with full stack traces

## Logged Components

### 1. Application Startup (`app/main.py`)
- Application startup/shutdown
- Configuration values (Redis URL, debug mode)
- Version information

### 2. Stream Service (`app/services/stream_service.py`)
- Stream creation and deletion
- Worker start/stop
- Reader initialization (RTSP, file, webcam)
- Model loading (YOLO, CSRNet)
- Frame processing loop
- Error counts and processing statistics

### 3. API Routes (`app/routes/streams.py`)
- HTTP requests (POST, GET, DELETE)
- Stream creation, stats retrieval, listing, deletion
- Error handling with full stack traces

### 4. YOLO Model (`core/models/yolo.py`)
- Model initialization
- Inference execution
- Detection counts
- Error handling

### 5. WebSocket (`app/ws/live.py`)
- Connection/disconnection events
- Redis pub/sub subscription
- Message sending statistics
- Error handling

### 6. Redis State (`core/state/redis_state.py`)
- Redis connection status
- Stats updates (Redis vs in-memory)
- Pub/sub publishing
- Error handling

## Log Format Examples

### Console Output
```
INFO - app.main - Starting Crowd Density API...
INFO - app.services.stream_service - Creating new stream: str_abc12345 (name: Camera 1)
INFO - app.services.stream_service - [str_abc12345] Starting stream worker...
INFO - app.services.stream_service - [str_abc12345] Initializing rtsp reader...
INFO - core.models.yolo - Initializing YOLO detector: model=yolov8n, conf=0.25, img_size=960
INFO - app.ws.live - WebSocket connected for stream str_abc12345 (total: 1)
```

### File Output (Detailed)
```
2025-01-15 10:30:45 - app.main - INFO - main.py:22 - Starting Crowd Density API...
2025-01-15 10:30:45 - app.services.stream_service - INFO - stream_service.py:244 - Creating new stream: str_abc12345 (name: Camera 1)
2025-01-15 10:30:45 - app.services.stream_service - ERROR - stream_service.py:55 - [str_abc12345] Failed to start reader: Connection refused
Traceback (most recent call last):
  File "stream_service.py", line 53, in start
    await self.reader.start()
  ...
```

## Viewing Logs

### Console
Logs are automatically printed to the console when running the backend.

### File
View the latest log file:
```bash
# Windows PowerShell
Get-Content backend\logs\crowd-density-*.log -Tail 50

# Linux/Mac
tail -f backend/logs/crowd-density-*.log
```

### Search Logs
```bash
# Find all errors
Select-String -Path "backend\logs\*.log" -Pattern "ERROR"

# Find logs for a specific stream
Select-String -Path "backend\logs\*.log" -Pattern "str_abc12345"
```

## Troubleshooting

### Common Log Messages

**Redis Not Available:**
```
WARNING - core.state.redis_state - Redis not available: Error 10061... Using in-memory fallback.
```
*Solution: Start Redis or ignore if using in-memory fallback*

**Model Loading Error:**
```
ERROR - core.models.yolo - Failed to load YOLO model yolov8n: ...
```
*Solution: Check model file exists, PyTorch compatibility*

**Stream Worker Error:**
```
ERROR - app.services.stream_service - [str_abc12345] Error processing frame 123: ...
```
*Solution: Check video source, frame format, model compatibility*

**WebSocket Error:**
```
ERROR - app.ws.live - Error sending WebSocket message for stream str_abc12345: ...
```
*Solution: Check client connection, message format*

## Configuration

Logging level can be changed in `app/main.py`:
```python
logger = setup_logging(logging.INFO)  # Change to logging.DEBUG for more detail
```

For production, consider:
- Using `logging.WARNING` to reduce log volume
- Setting up log aggregation (ELK, Loki, etc.)
- Implementing log rotation policies
- Adding structured logging (JSON format)

