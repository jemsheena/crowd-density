# Crowd Density Estimation

Real-time video analysis system that counts people and generates density heatmaps from video streams. Supports RTSP cameras, video files, and webcams.

## What It Does

- Counts people in real-time from video feeds
- Generates density heatmaps overlaid on video
- Supports multiple video sources (RTSP, files, webcams)
- Zone-based counting with threshold alerts
- WebSocket-based live updates
- Hybrid model selection (YOLO for sparse, CSRNet for dense crowds)

## Tech Stack

**Backend:**
- FastAPI (Python)
- PyTorch, YOLOv8, CSRNet
- Redis (state management, pub/sub)
- OpenCV (video processing)

**Frontend:**
- React + Vite
- Tailwind CSS
- Zustand (state)
- WebSocket client

## Getting Started

### Prerequisites

- Python 3.11+ (3.13 works)
- Node.js 18+
- Redis (optional but recommended)

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Backend runs on `http://localhost:8000`. API docs at `/docs`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs on `http://localhost:5173`.

### Redis (Recommended)

For full functionality, start Redis:

**With Docker:**
```bash
docker run -d -p 6379:6379 --name redis redis:7-alpine
```

**Without Docker:**
- Windows: Install [Memurai](https://www.memurai.com/get-memurai) (free)
- Or use native Redis from [tporadowski/redis](https://github.com/tporadowski/redis/releases)

The backend works without Redis but with limited functionality (no real-time updates, no state persistence).

## Configuration

Default settings work out of the box. To customize, create `.env` files:

**Backend** (`backend/.env`):
```
REDIS_URL=redis://localhost:6379/0
MODEL_DIR=./models
DEBUG=false
```

**Frontend** (`frontend/.env`):
```
VITE_API_URL=http://localhost:8000
```

See `backend/app/config.py` for all available settings.

## API

### REST Endpoints

- `POST /streams` - Create stream
- `GET /streams` - List streams
- `GET /streams/{id}/stats` - Get stats
- `DELETE /streams/{id}` - Delete stream

### WebSocket

- `WS /ws/streams/{id}/live` - Live updates (10-20 Hz)

See `http://localhost:8000/docs` for full API documentation.

## Models

**YOLOv8n** - Person detection for sparse to medium density. Auto-downloads on first use.

**CSRNet** - Density estimation for high-density crowds. Stub implementation included.

**Hybrid Selector** - Automatically switches between models based on scene complexity (Laplacian variance).

## Project Structure

```
backend/
  app/              # FastAPI app, routes, services
  core/
    ingestion/      # RTSP/file/webcam readers
    models/         # YOLO and CSRNet wrappers
    orchestrator/   # Hybrid selector, pipeline
    postprocess/    # Smoothing, zones, heatmaps
    state/          # Redis state management

frontend/
  src/
    components/     # React components
    pages/          # Route pages
    store/          # Zustand stores
    api/            # API client
```

## Development

### Adding a Video Source

1. Create reader in `backend/core/ingestion/`
2. Implement async `frames()` generator
3. Register in `backend/app/services/stream_service.py`

### Adding a Model

1. Create wrapper in `backend/core/models/`
2. Implement `infer(image)` method returning count/density map
3. Register in `backend/core/orchestrator/pipeline.py`

### Logging

Logs written to `backend/logs/crowd-density-YYYYMMDD.log` and console. See `backend/LOGGING.md` for details.

## Docker

```bash
cd deploy
docker-compose -f docker-compose.dev.yml up
```

Starts Redis, MinIO, Prometheus, and Grafana. Backend and frontend still run locally.

## Troubleshooting

**Backend won't start:**
- Check Python version: `python --version`
- Verify dependencies: `pip install -r requirements.txt`
- Check port 8000 isn't in use

**Redis connection errors:**
- Verify Redis is running: `redis-cli ping` (or `python -c "import redis; r=redis.from_url('redis://localhost:6379/0'); print(r.ping())"`)
- Check `REDIS_URL` in `.env`
- Backend works without Redis (with warnings)

**No video frames:**
- Check video file path is correct
- Verify RTSP URL is accessible
- Check webcam device index (usually 0)
- See logs in `backend/logs/` for errors

**Model loading errors:**
- YOLOv8 auto-downloads, CSRNet needs weights
- Check `MODEL_DIR` path exists
- PyTorch 2.6+ requires compatible model weights

## License

MIT
