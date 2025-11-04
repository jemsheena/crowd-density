# Redis Setup for Windows

## Quick Setup Options

### Option 1: Memurai (Recommended - Easiest) ⭐

**Memurai is a Redis-compatible server for Windows. Free for development.**

1. **Download Memurai:**
   - Visit: https://www.memurai.com/get-memurai
   - Download the free Developer Edition
   - Run the installer

2. **Start Memurai:**
   - Memurai installs as a Windows service
   - It starts automatically on boot
   - Runs on port 6379 (same as Redis)

3. **Verify it's running:**
   ```powershell
   python -c "import redis; r = redis.from_url('redis://localhost:6379/0'); print('Redis OK!' if r.ping() else 'Not running')"
   ```

**That's it!** Your backend will now connect to Redis automatically.

---

### Option 2: Windows Native Redis

**Use the official Windows Redis build:**

1. **Download Redis:**
   - Visit: https://github.com/tporadowski/redis/releases
   - Download latest `Redis-x64-*.zip` (e.g., `Redis-x64-5.0.14.1.zip`)
   - Extract to `C:\Redis`

2. **Start Redis:**
   ```powershell
   cd C:\Redis
   redis-server.exe
   ```

3. **Keep this window open** - Redis runs in the foreground

4. **In a new terminal**, start your backend:
   ```powershell
   cd backend
   uvicorn app.main:app --reload
   ```

---

### Option 3: Install Docker Desktop (Then Redis)

1. **Download Docker Desktop:**
   - Visit: https://www.docker.com/products/docker-desktop
   - Install Docker Desktop

2. **Start Redis container:**
   ```powershell
   docker run -d -p 6379:6379 --name redis redis:7-alpine
   ```

3. **Verify:**
   ```powershell
   docker ps
   # Should show redis container running
   ```

---

## ✅ Recommended: Memurai (Option 1)

**Why Memurai?**
- ✅ Free for development
- ✅ Runs as Windows service (auto-starts)
- ✅ No need to keep terminal open
- ✅ Fully Redis-compatible
- ✅ Easy installation

**Steps:**
1. Download from https://www.memurai.com/get-memurai
2. Install (default settings)
3. Done! Redis will be available at `localhost:6379`

---

## Verify Redis is Running

After setup, test the connection:

```powershell
python -c "import redis; r = redis.from_url('redis://localhost:6379/0'); print('✅ Redis OK!' if r.ping() else '❌ Redis not running')"
```

Or in Python:
```python
import redis
r = redis.from_url('redis://localhost:6379/0')
print(r.ping())  # Should print: True
```

---

## Start Your System

Once Redis is running:

**Terminal 1 - Backend:**
```powershell
cd backend
uvicorn app.main:app --reload
```

**Terminal 2 - Frontend:**
```powershell
cd frontend
npm run dev
```

You should see:
- ✅ No Redis warnings in backend logs
- ✅ `INFO - Redis connected successfully` in logs
- ✅ WebSocket connections working
- ✅ Real-time updates in frontend

---

## Troubleshooting

### Redis connection refused
- Make sure Redis/Memurai is running
- Check port 6379 is not blocked by firewall
- Verify Redis is listening: `netstat -an | findstr 6379`

### Memurai not starting
- Check Windows Services: `services.msc`
- Look for "Memurai" service
- Start it if stopped

### Port already in use
- Another Redis instance might be running
- Check: `netstat -ano | findstr 6379`
- Stop the other instance or use a different port

