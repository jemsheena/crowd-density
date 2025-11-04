# Setup Options for Crowd Density System

## 🎯 Docker is NOT Required

The system can run without Docker, but Redis is needed for full functionality.

---

## Option 1: Full Setup (Redis + Docker) ✅ Recommended

**Best for:** Production-like setup, easiest Redis management

```powershell
# Start Redis with Docker
docker run -d -p 6379:6379 --name redis redis:7-alpine

# Start backend
cd backend
uvicorn app.main:app --reload

# Start frontend
cd frontend
npm run dev
```

**Pros:**
- ✅ Easiest Redis setup
- ✅ Full functionality (pub/sub, state persistence)
- ✅ Production-ready

**Cons:**
- ❌ Requires Docker Desktop

---

## Option 2: Redis Without Docker (Windows Native)

**Best for:** Windows users without Docker

### Install Redis for Windows:

1. **Download Redis:**
   - Visit: https://github.com/microsoftarchive/redis/releases
   - Download latest `Redis-x64-*.zip`
   - Extract to `C:\Redis`

2. **Start Redis:**
   ```powershell
   cd C:\Redis
   redis-server.exe
   ```

3. **Start backend and frontend** (same as Option 1)

**Pros:**
- ✅ No Docker needed
- ✅ Full functionality
- ✅ Native Windows

**Cons:**
- ❌ Manual installation
- ❌ Need to manage Redis service

---

## Option 3: Redis with WSL2

**Best for:** Windows users who want Linux Redis

```powershell
# Install WSL2 (if not already)
wsl --install

# In WSL2 terminal:
sudo apt-get update
sudo apt-get install redis-server
sudo service redis-server start

# Redis will be available at localhost:6379
```

**Pros:**
- ✅ Full functionality
- ✅ Linux-native Redis
- ✅ Good for development

**Cons:**
- ❌ Requires WSL2 setup
- ❌ More complex setup

---

## Option 4: Run WITHOUT Redis (Limited Functionality) ⚠️

**Best for:** Quick testing, UI development

```powershell
# Start backend (will show Redis warnings)
cd backend
uvicorn app.main:app --reload

# Start frontend
cd frontend
npm run dev
```

**What works:**
- ✅ Backend starts
- ✅ API endpoints work
- ✅ Can create streams
- ✅ UI loads

**What doesn't work:**
- ❌ No real-time updates (WebSocket limited)
- ❌ No state persistence (restart = lose data)
- ❌ No pub/sub (multi-client won't sync)
- ❌ Streams won't process properly

**Note:** The system uses in-memory fallback, but stream processing requires Redis for pub/sub.

---

## 🚀 Quick Start (Recommended Path)

### Minimum Setup (Testing):
1. **Skip Redis for now** - Backend will start with warnings
2. Test UI and basic functionality
3. Add Redis later when needed

### Full Setup (Production-ready):
1. **Install Docker Desktop** (if not installed)
2. **Start Redis:** `docker run -d -p 6379:6379 redis:7-alpine`
3. **Start backend:** `uvicorn app.main:app --reload`
4. **Start frontend:** `npm run dev`

---

## 📋 System Requirements

### Required:
- ✅ Python 3.11+ (or 3.13)
- ✅ Node.js 18+
- ✅ All Python packages installed (`pip install -r requirements.txt`)
- ✅ All Node packages installed (`npm install`)

### Recommended (for full functionality):
- ✅ Redis (via Docker, Windows native, or WSL2)
- ✅ Docker Desktop (easiest Redis setup)

### Optional:
- ✅ Docker Compose (for full stack)
- ✅ Prometheus/Grafana (for metrics)

---

## 🔍 Check What You Have

```powershell
# Check Python
python --version

# Check Node
node --version

# Check Docker (optional)
docker --version

# Check Redis connection
python -c "import redis; r = redis.from_url('redis://localhost:6379/0'); print('Redis OK' if r.ping() else 'Redis not running')"
```

---

## 💡 Recommendation

**For Development:**
- Start with **Option 4** (no Redis) to test UI
- Add **Option 1** (Docker + Redis) when ready for real processing

**For Production:**
- Use **Option 1** (Docker + Redis) or **Option 2** (Windows Redis)
- Consider Docker Compose for full stack

**Bottom line:** Docker is **convenient** but **not required**. Redis is **needed for full functionality** but the system will **start without it** (with limited features).

