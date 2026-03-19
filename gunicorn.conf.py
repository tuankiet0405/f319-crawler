# Gunicorn configuration for Render deployment
# This file is auto-detected by gunicorn

bind = "0.0.0.0:10000"
workers = 1               # MUST be 1: in-memory job store requires single process
threads = 4               # handle concurrent requests via threads instead
timeout = 30              # endpoints return instantly (background jobs)
keepalive = 5
accesslog = "-"
errorlog = "-"
