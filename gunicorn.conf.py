# Gunicorn configuration for Render deployment
# This file is auto-detected by gunicorn

bind = "0.0.0.0:10000"
workers = 2
timeout = 120          # crawling can take 60s+
keepalive = 5
accesslog = "-"
errorlog = "-"
