# Docker Setup for Windows

## 🐳 Installing Docker Desktop

### Step 1: Download Docker Desktop

1. **Visit the official Docker website:**
   - Go to: https://www.docker.com/products/docker-desktop
   - Or direct download: https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe

2. **System Requirements:**
   - Windows 10 64-bit: Pro, Enterprise, or Education (Build 19041 or higher)
   - Windows 11 64-bit
   - WSL 2 feature enabled (Docker Desktop will enable this automatically)
   - Virtualization enabled in BIOS

### Step 2: Install Docker Desktop

1. **Run the installer:**
   - Double-click `Docker Desktop Installer.exe`
   - Follow the installation wizard
   - ✅ Check "Use WSL 2 instead of Hyper-V" (recommended)
   - ✅ Check "Add shortcut to desktop"

2. **Restart when prompted:**
   - Windows will restart to enable WSL 2 if needed
   - After restart, Docker Desktop should start automatically

3. **Accept the service agreement** when Docker Desktop launches

### Step 3: Verify Installation

Open PowerShell and run:

```powershell
docker --version
# Should show: Docker version 24.x.x or higher

docker ps
# Should show: CONTAINER ID   IMAGE   COMMAND   CREATED   STATUS   PORTS   NAMES
# (Empty list is fine - no containers running yet)
```

---

## 🚀 Setting Up Redis with Docker

Once Docker is installed, start Redis:

### Start Redis Container

```powershell
docker run -d -p 6379:6379 --name redis-crowd-density redis:7-alpine
```

**What this does:**
- `-d`: Run in detached mode (background)
- `-p 6379:6379`: Map port 6379 (host) to 6379 (container)
- `--name redis-crowd-density`: Name the container
- `redis:7-alpine`: Use Redis 7 Alpine image (lightweight)

### Verify Redis is Running

```powershell
# Check if container is running
docker ps

# Should show:
# CONTAINER ID   IMAGE           COMMAND                  CREATED         STATUS         PORTS                    NAMES
# abc123def456   redis:7-alpine   "docker-entrypoint.s…"   5 seconds ago   Up 5 seconds   0.0.0.0:6379->6379/tcp   redis-crowd-density

# Test Redis connection
python -c "import redis; r = redis.from_url('redis://localhost:6379/0'); print('✅ Redis OK!' if r.ping() else '❌ Redis not working')"
```

### Redis Management Commands

```powershell
# Stop Redis
docker stop redis-crowd-density

# Start Redis (if stopped)
docker start redis-crowd-density

# Remove Redis container
docker rm redis-crowd-density

# View Redis logs
docker logs redis-crowd-density

# Restart Redis
docker restart redis-crowd-density
```

---

## 🎯 Complete Setup Workflow

### 1. Install Docker Desktop
- Download from https://www.docker.com/products/docker-desktop
- Install and restart if needed
- Wait for Docker Desktop to start (whale icon in system tray)

### 2. Start Redis
```powershell
docker run -d -p 6379:6379 --name redis-crowd-density redis:7-alpine
```

### 3. Verify Everything Works
```powershell
# Check Docker
docker ps

# Check Redis
python -c "import redis; r = redis.from_url('redis://localhost:6379/0'); print('✅ Redis OK!' if r.ping() else '❌ Redis not working')"
```

### 4. Start Your Backend
```powershell
cd backend
uvicorn app.main:app --reload
```

You should now see:
- ✅ `INFO - Redis connected successfully: redis://localhost:6379/0`
- ✅ No Redis warnings
- ✅ WebSocket connections working

---

## 🔧 Troubleshooting

### Docker Desktop won't start
- **WSL 2 not installed:**
  ```powershell
  wsl --install
  ```
  Restart after installation

- **Virtualization disabled:**
  - Enter BIOS/UEFI settings
  - Enable "Virtualization Technology" or "VT-x"
  - Save and restart

- **Hyper-V conflicts:**
  - Disable Hyper-V in Windows Features
  - Use WSL 2 instead (recommended)

### Docker command not found
- Make sure Docker Desktop is running
- Restart PowerShell/terminal
- Check PATH: Docker should be in system PATH

### Port 6379 already in use
```powershell
# Find what's using port 6379
netstat -ano | findstr 6379

# Stop the process or use different port:
docker run -d -p 6380:6379 --name redis-crowd-density redis:7-alpine
# Then update REDIS_URL in backend/.env to: redis://localhost:6380/0
```

### Redis container keeps stopping
```powershell
# Check logs
docker logs redis-crowd-density

# Check container status
docker ps -a
```

---

## 📝 Docker Compose (Optional - Advanced)

For a complete stack with Redis, MinIO, Prometheus, etc.:

```powershell
cd deploy
docker-compose -f docker-compose.dev.yml up -d
```

This starts:
- ✅ Redis on port 6379
- ✅ MinIO on port 9000
- ✅ Prometheus on port 9090
- ✅ Grafana on port 3000

---

## ✅ Quick Reference

**Start Redis:**
```powershell
docker run -d -p 6379:6379 --name redis-crowd-density redis:7-alpine
```

**Stop Redis:**
```powershell
docker stop redis-crowd-density
```

**Start Redis (after stopping):**
```powershell
docker start redis-crowd-density
```

**Remove Redis:**
```powershell
docker stop redis-crowd-density
docker rm redis-crowd-density
```

**View Redis logs:**
```powershell
docker logs -f redis-crowd-density
```

---

## 🎉 Next Steps

Once Docker and Redis are running:

1. **Start Backend:**
   ```powershell
   cd backend
   uvicorn app.main:app --reload
   ```

2. **Start Frontend:**
   ```powershell
   cd frontend
   npm run dev
   ```

3. **Open Browser:**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

You should now have full functionality with real-time updates!

