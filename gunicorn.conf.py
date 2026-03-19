# Gunicorn configuration for Render deployment
import os

# Bind to Render's PORT (required)
bind = f"0.0.0.0:{os.environ.get('PORT', '10000')}"

# Single worker + threads (required for in-memory job store)
workers = 1
threads = 4
worker_class = "gthread"

# Timeout — endpoints return instantly with background jobs
timeout = 30
keepalive = 5

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Preload app to catch import errors early
preload_app = True
