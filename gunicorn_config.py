import os
from dotenv import load_dotenv
load_dotenv()
# Get PORT from environment variable with fallback to 5000
# Render sets the PORT environment variable for web services
raw_port = os.getenv("PORT")
port = int(raw_port) if raw_port is not None else 5000
print(f"PORT environment variable: {raw_port}")
print(f"Using PORT: {port}")

# Bind to the correct host and port - CRITICAL for Render to detect the service
# This must be in the format 0.0.0.0:PORT for Render to properly detect it
bind = f"0.0.0.0:{port}"
print(f"Binding to: {bind}")

# Explicitly log binding information for debugging
import socket
def post_fork(server, worker):
    print(f"Worker forked! Binding to {bind}")
    # Create a test socket to ensure binding works
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(("0.0.0.0", 0))  # Bind to a random port to test socket creation
        print(f"Socket test successful, random port: {s.getsockname()[1]}")
        s.close()
    except Exception as e:
        print(f"Socket test failed: {e}")

# Ensure socket is created early in the startup process
print("Testing socket binding capability...")
try:
    test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    test_socket.bind(("0.0.0.0", 0))  # Bind to a random port
    print(f"Pre-startup socket test successful on random port: {test_socket.getsockname()[1]}")
    test_socket.close()
except Exception as e:
    print(f"Pre-startup socket test failed: {e}")
workers = 2
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