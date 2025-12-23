# Gunicorn configuration file for Render deployment
# Optimized for Server-Sent Events (SSE) streaming

import multiprocessing
import os

# Server socket
bind = f"0.0.0.0:{os.getenv('PORT', '5000')}"
backlog = 2048

# Worker processes
workers = 1  # Use 1 worker for in-memory progress_store to work correctly
worker_class = 'sync'  # Use sync worker for SSE
threads = 4  # Number of threads per worker
worker_connections = 1000
max_requests = 0  # Disable worker restart after N requests
max_requests_jitter = 0
timeout = 0  # No timeout for long-running SSE connections
graceful_timeout = 30
keepalive = 75  # Keep connections alive for 75 seconds

# Logging
accesslog = '-'  # Log to stdout
errorlog = '-'   # Log to stderr
loglevel = 'info'
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process naming
proc_name = 'dpdp_compliance_checker'

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# SSL (for HTTPS - Render handles this, so we don't need it here)
keyfile = None
certfile = None

# Response buffering - CRITICAL for SSE
# Disable response buffering to ensure real-time streaming
worker_tmp_dir = '/dev/shm'  # Use shared memory for worker tmp dir (faster)

# Preload app
preload_app = False  # Don't preload - we need fresh app per worker

# Server hooks
def on_starting(server):
    """Called just before the master process is initialized."""
    server.log.info("Gunicorn server starting...")

def when_ready(server):
    """Called just after the server is started."""
    server.log.info("Gunicorn server is ready to handle requests")

def on_reload(server):
    """Called to recycle workers during a reload via SIGHUP."""
    server.log.info("Gunicorn server reloading...")

def worker_int(worker):
    """Called when a worker receives SIGINT or SIGQUIT."""
    worker.log.info("Worker received INT or QUIT signal")

def worker_abort(worker):
    """Called when a worker receives SIGABRT signal."""
    worker.log.info("Worker received SIGABRT signal")
