import os

# Get the PORT environment variable or use 8502 as the default
port = int(os.environ.get("PORT", 8502))

bind = f"0.0.0.0:{port}"
workers = 1
threads = 8
timeout = 120