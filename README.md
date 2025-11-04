# Crowd Density Estimation System

An AI-based software that watches video feeds and tells you how crowded each area is — showing real-time heatmaps, counts, and alerts for safer crowd management.

## 🏗️ Architecture

```
Frontend (React/Tailwind) ←→ WebSocket/REST ←→ FastAPI Gateway
                                              ↓
                         Ingestion ←→ Orchestrator ←→ Models (YOLO/CSRNet)
                                              ↓
                         Redis (State) ←→ Prometheus (Metrics)
```

## 📦 Repository Structure

```
crowd-density/
├── frontend/                 # React + Vite + Tailwind
│   ├── src/
│   │   ├── components/      # StreamCard, HeatmapCanvas, ZoneEditor, AlertBanner
│   │   ├── pages/           # Dashboard, StreamDetail, Settings, Auth
│   │   ├── store/           # Zustand state management
│   │   └── api/             # REST + WebSocket clients
├── backend/
│   ├── app/                 # FastAPI gateway
│   │   ├── main.py          # App factory
│   │   ├── routes/          # API routes
│   │   ├── dto/             # Pydantic models
│   │   ├── ws/              # WebSocket endpoints
│   │   └── config.py        # Settings
│   ├── core/
│   │   ├── ingestion/       # RTSP/file/webcam readers
│   │   ├── models/          # YOLO + CSRNet wrappers
│   │   ├── orchestrator/    # Hybrid selector + pipeline
│   │   ├── postprocess/     # Smoothing + zones
│   │   └── metrics/          # Prometheus instrumentation
│   └── docker/              # Dockerfiles
└── deploy/
    └── docker-compose.dev.yml
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+ (or 3.13)
- Node.js 18+
- Redis (optional but recommended - see setup options below)
- Docker (optional - only needed for easy Redis setup)

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Optional: Start Redis (recommended for full functionality)
# Option 1: Docker
docker run -d -p 6379:6379 redis:7-alpine

# Option 2: Windows Redis (download from GitHub releases)
# Option 3: Skip Redis (limited functionality - backend will start with warnings)

# Run server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Note:** Redis is optional but recommended. The backend will start without it but with limited functionality. See `SETUP_OPTIONS.md` for detailed setup instructions.

### Frontend Setup

```bash
cd frontend
npm install

# Copy environment file
cp .env.example .env

# Run dev server
npm run dev
```

### Docker Setup

```bash
# From project root
cd deploy
docker-compose -f docker-compose.dev.yml up
```

## 📡 API Endpoints

### REST API

- `POST /streams` - Create a new stream
- `GET /streams` - List all streams
- `GET /streams/{id}/stats` - Get stream statistics
- `POST /infer` - Run inference on uploaded image
- `GET /metrics` - Prometheus metrics

### WebSocket

- `WS /ws/streams/{id}/live` - Live stream updates (10-20 Hz)

## 🔧 Configuration

See `backend/.env.example` and `frontend/.env.example` for configuration options.

Key settings:
- `AUTH_DISABLED=true` - Disable auth for development
- `REDIS_URL` - Redis connection string
- `S3_ENDPOINT_URL` - S3/MinIO endpoint
- `MODEL_DIR` - Path to model weights

## 🧠 Models

### YOLOv8
- Detector for sparse-medium density scenes
- Provides bounding boxes for ROI analysis
- Auto-downloads weights on first use

### CSRNet
- Density estimation for high-density scenes
- Outputs density maps (sum ≈ count)
- Requires trained weights (stub included)

### Hybrid Selector
- Automatically chooses model based on scene characteristics
- Uses Laplacian variance as scene complexity metric
- Hysteresis prevents frequent toggling

## 📊 Features

- ✅ Real-time crowd counting
- ✅ Heatmap visualization
- ✅ Zone-based counting and alerts
- ✅ Temporal smoothing (EMA)
- ✅ WebSocket live updates
- ✅ Prometheus metrics
- ✅ REST API
- ✅ Docker support

## 🧪 Testing

```bash
# Backend tests (to be implemented)
cd backend
pytest

# Frontend tests (to be implemented)
cd frontend
npm test
```

## 📈 Monitoring

- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (admin/admin)
- API Docs: http://localhost:8000/docs

## 🔒 Security

- JWT authentication (configurable)
- CORS protection
- Rate limiting
- Input validation

## 📝 Development

### Adding a New Stream Source

1. Create reader in `backend/core/ingestion/`
2. Implement async `frames()` iterator
3. Register in stream service

### Adding a New Model

1. Create wrapper in `backend/core/models/`
2. Implement `infer(image)` method
3. Register in orchestrator

## 🚧 TODO

- [ ] Implement full CSRNet architecture and training
- [ ] Add Redis pub/sub for WebSocket
- [ ] Add database persistence (PostgreSQL)
- [ ] Add authentication endpoints
- [ ] Add unit tests
- [ ] Add E2E tests
- [ ] Add model registry
- [ ] Add training pipeline

## 📄 License

MIT
