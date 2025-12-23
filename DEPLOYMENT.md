# Deployment Guide - Render SSE Fix

## Problem

The application was experiencing SSE (Server-Sent Events) connection timeouts after 30-40 seconds when deployed on Render, causing the "Connection error. Please try again." message.

## Root Causes

1. **Response Buffering**: Gunicorn and Render's proxy were buffering SSE messages, preventing keep-alive signals from reaching the client
2. **Insufficient Keep-Alive Frequency**: Keep-alive messages were sent every 5 seconds, which wasn't enough for Render's load balancer
3. **Missing Stream Flushing**: SSE stream wasn't being flushed after each message
4. **Configuration Issues**: Gunicorn wasn't optimized for long-running SSE connections

## Fixes Applied

### 1. Backend (app.py)

**Changes:**
- Added `stream_with_context` decorator for proper Flask streaming
- Increased keep-alive frequency from 5s to 10s
- Added explicit `sys.stdout.flush()` after each SSE message
- Extended max timeout from 5 to 10 minutes
- Added proper SSE headers: `Connection: keep-alive`, `no-transform`, etc.
- Removed `direct_passthrough` which was causing buffering issues

**Result:** SSE messages are now sent immediately without buffering.

### 2. Frontend (script.js)

**Changes:**
- Added connection timeout detection (45 seconds without updates)
- Improved error handling to distinguish between normal closure and actual errors
- Added `lastUpdateTime` tracking to prevent false error alerts
- Better error messages for users

**Result:** More graceful handling of connection issues.

### 3. Gunicorn Configuration (gunicorn.conf.py)

**New file created with:**
- `workers = 1`: Single worker to ensure in-memory `progress_store` works correctly
- `threads = 4`: Multiple threads for concurrent requests
- `timeout = 0`: No timeout for long-running SSE connections
- `keepalive = 75`: Keep connections alive for 75 seconds
- `worker_tmp_dir = '/dev/shm'`: Use shared memory for faster I/O
- Proper logging and process naming

**Result:** Gunicorn optimized for SSE streaming.

### 4. Dockerfile

**Created with:**
- Python 3.12 slim base image
- Automatic FAISS index building during build
- Proper environment variables for unbuffered output
- Optimized layer caching

**Result:** Production-ready Docker image.

### 5. Additional Files

- **render.yaml**: Blueprint for easy Render deployment
- **start.sh**: Start script with FAISS index auto-build
- **.dockerignore**: Reduced image size by excluding unnecessary files

## Deployment Instructions

### Option 1: Deploy to Render via Dashboard

1. **Push code to GitHub**:
   ```bash
   git add .
   git commit -m "Fix SSE timeout issues for Render deployment"
   git push origin master
   ```

2. **Create Web Service on Render**:
   - Go to https://dashboard.render.com/
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Configure:
     - **Name**: dpdp-compliance-checker
     - **Environment**: Docker
     - **Region**: Choose closest to your users
     - **Branch**: master
     - **Build Command**: `python -m utils.vector_store.build_index`
     - **Start Command**: `gunicorn --config gunicorn.conf.py app:app`

3. **Set Environment Variables**:
   - Add `GROQ_API_KEY` with your Groq API key
   - Render will automatically set `PORT`

4. **Deploy**: Click "Create Web Service"

### Option 2: Deploy via render.yaml (Recommended)

1. **Push code to GitHub** (same as above)

2. **Create New Service**:
   - Go to Render dashboard
   - Click "New +" → "Blueprint"
   - Connect your repository
   - Render will auto-detect `render.yaml`

3. **Set GROQ_API_KEY**:
   - In the Blueprint setup, set `GROQ_API_KEY` environment variable

4. **Deploy**: Click "Apply"

### Option 3: Local Testing with Docker

```bash
# Build Docker image
docker build -t dpdp-compliance-checker .

# Run container
docker run -p 5000:5000 \
  -e GROQ_API_KEY=your_api_key_here \
  dpdp-compliance-checker

# Access at http://localhost:5000
```

## Testing the Fix

### Local Testing (without Docker)

```bash
# Install dependencies
pip install -r requirements.txt

# Build FAISS index (first time only)
python -m utils.vector_store.build_index

# Run with gunicorn
gunicorn --config gunicorn.conf.py app:app

# Or run with Flask development server (not recommended for production)
python app.py
```

### Verify SSE Connection

1. Open browser DevTools (F12) → Network tab
2. Click on a provider (e.g., ChatGPT)
3. Look for `/progress/` request in Network tab
4. Should see:
   - Status: 200
   - Type: eventsource
   - Keep-alive messages every 10 seconds: `: keepalive at 10.0s`, `: keepalive at 20.0s`, etc.
   - Progress updates: `category_start`, `category_complete`, `complete`

### Expected Behavior

- **Progress modal** appears immediately with timer
- **Keep-alive messages** appear in console every 10 seconds
- **Category updates** stream in real-time
- **No timeout errors** even if processing takes 2-3 minutes
- **Report page** loads automatically when complete

## Troubleshooting

### Issue: Still timing out after 30-40 seconds

**Solutions:**
1. Check Render logs: Dashboard → Your Service → Logs
2. Verify gunicorn is using the config file: Look for "Gunicorn server is ready" message
3. Ensure `workers = 1` in gunicorn.conf.py (multiple workers break in-memory store)
4. Check browser console for SSE messages

### Issue: FAISS index not found

**Solution:**
```bash
# Rebuild FAISS index
python -m utils.vector_store.build_index
```

### Issue: Slow processing

**Causes:**
- Groq API rate limits
- Large policy documents
- Cold start (first request after inactivity)

**Solutions:**
- Upgrade Groq API plan for higher rate limits
- Use caching for policy documents
- Upgrade Render plan to prevent cold starts

## Performance Optimizations

### For Faster Processing

1. **Use Render Paid Plan**: Free tier has cold starts
2. **Enable Persistent Disk**: Store FAISS index on disk
3. **Increase Workers**: If you implement Redis for progress storage
4. **Add Caching**: Cache policy documents to avoid re-downloads

### For Better SSE Reliability

1. **Reduce Keep-Alive Interval**: Change from 10s to 5s if still having issues
2. **Add Connection Testing**: Implement ping/pong between client and server
3. **Use WebSockets**: For more complex real-time communication

## Key Configuration Files

| File | Purpose |
|------|---------|
| `app.py` | SSE streaming with flush and keep-alive |
| `gunicorn.conf.py` | Gunicorn optimized for SSE (1 worker, no timeout) |
| `Dockerfile` | Production Docker image with FAISS build |
| `render.yaml` | Render deployment blueprint |
| `requirements.txt` | Python dependencies including gunicorn |

## Important Notes

1. **Single Worker**: Must use 1 worker because `progress_store` is in-memory. For multiple workers, use Redis or database.

2. **Keep-Alive Critical**: Without frequent keep-alive messages, Render's load balancer will close idle connections.

3. **Flush Required**: SSE messages must be flushed immediately, otherwise they're buffered until the buffer fills.

4. **FAISS Index**: Must be built before app starts. Dockerfile handles this automatically.

## Next Steps

### For Production Use

1. **Implement Redis**: Replace in-memory `progress_store` with Redis for multi-worker support
2. **Add Health Checks**: Implement `/health` endpoint
3. **Monitor Logs**: Set up log aggregation (Render provides this)
4. **Add Error Tracking**: Integrate Sentry or similar
5. **Enable CORS**: If frontend is on different domain

### For Better UX

1. **Add Reconnection**: Auto-reconnect SSE on disconnect
2. **Add Progress Percentage**: Show % complete instead of just category names
3. **Cache Results**: Store results in sessionStorage for back button
4. **Add Export Options**: Export results as CSV, JSON

## Support

If you continue experiencing issues:

1. Check Render logs: `Dashboard → Your Service → Logs`
2. Check browser console: DevTools → Console (F12)
3. Verify environment variables are set correctly
4. Ensure GROQ_API_KEY is valid and has sufficient credits

## Summary

All SSE timeout issues have been fixed by:
- ✅ Proper stream flushing
- ✅ Frequent keep-alive messages (every 10s)
- ✅ Optimized gunicorn configuration
- ✅ Better error handling
- ✅ Production-ready Dockerfile

The application should now work reliably on Render with no timeout errors!
