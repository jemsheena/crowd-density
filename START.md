# How to Start the Crowd Density Estimation System

## Prerequisites
- Python 3.13 (or 3.11/3.12) installed
- Node.js 18+ installed
- All dependencies installed (see below)

## Quick Start

### 1. Start the Backend (FastAPI)

Open a terminal/PowerShell window and run:

```powershell
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The backend will start at:
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

### 2. Start the Frontend (React)

Open a **new** terminal/PowerShell window and run:

```powershell
cd frontend
npm run dev
```

The frontend will start at:
- **Frontend**: http://localhost:5173

## Detailed Setup

### Backend Setup (if not done)

```powershell
cd backend

# Create virtual environment (optional but recommended)
python -m venv venv
.\venv\Scripts\activate  # On Windows
# source venv/bin/activate  # On Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Start server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup (if not done)

```powershell
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

## Using Docker (Alternative)

If you prefer Docker:

```powershell
cd deploy
docker-compose -f docker-compose.dev.yml up
```

This starts:
- API on http://localhost:8000
- Redis on localhost:6379
- MinIO on http://localhost:9000
- Prometheus on http://localhost:9090
- Grafana on http://localhost:3000

## Access Points

Once both servers are running:

1. **Frontend Dashboard**: http://localhost:5173
2. **Backend API**: http://localhost:8000
3. **API Documentation**: http://localhost:8000/docs
4. **Health Check**: http://localhost:8000/health

## Troubleshooting

### Backend won't start
- Make sure port 8000 is not in use
- Check that all Python dependencies are installed
- Verify Python version (3.13, 3.12, or 3.11)

### Frontend won't start
- Make sure port 5173 is not in use
- Run `npm install` in the frontend directory
- Check Node.js version (18+)

### Connection errors
- Make sure backend is running before starting frontend
- Check that CORS is configured correctly in `backend/app/config.py`
- Verify API_BASE and WS_BASE in frontend `.env` file (if using)

## Next Steps

1. Open http://localhost:5173 in your browser
2. Create a stream via the dashboard (click "+ Create Stream")
3. View real-time crowd density estimation
4. Draw zones and set thresholds
5. Monitor alerts and live stats
6. Check API docs at http://localhost:8000/docs

**See `USER_GUIDE.md` for detailed usage instructions.**

