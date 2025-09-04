from dotenv import load_dotenv
import os
load_dotenv()
# Get PORT from environment variable with fallback to 8502
# Render sets the PORT environment variable for web services
raw_port = os.getenv("PORT")
port = int(raw_port) if raw_port is not None else 8502
print(f"PORT environment variable: {raw_port}")
print(f"Using PORT: {port}")

# Bind to the correct host and port
bind = f"0.0.0.0:{port}"
workers = 1
threads = 4
timeout = 180
max_requests = 1000
max_requests_jitter = 50
worker_class = 'sync'
worker_tmp_dir = '/tmp'
worker_connections = 1000
keepalive = 2
# Memory optimization
preload_app = False