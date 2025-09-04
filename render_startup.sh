#!/bin/bash

# Set environment variables for production
export FLASK_ENV="production"

# Set memory optimization environment variables
export PYTHONUNBUFFERED=1
export PYTHONHASHSEED=random

# Create necessary directories
mkdir -p artifacts
mkdir -p data/user_interactions

# Check if model files exist
if [ ! -f "artifacts/movie_list.pkl" ] || [ ! -f "artifacts/similarity.pkl" ]; then
    echo "Model files not found. Running initial training..."
    # Download datasets if needed
    python download_datasets.py
    # Run initial model training with memory optimization
    python -m src.scripts.retrain_model --initial-train
    echo "Initial training completed."
fi

# Clean up memory before starting the server
echo "Cleaning up memory..."
sync
echo 3 > /proc/sys/vm/drop_caches 2>/dev/null || true

# Ensure PORT environment variable is set (Render should set this automatically)
if [ -z "${PORT}" ]; then
    echo "PORT environment variable not set, using default 10000"
    export PORT=10000
fi
echo "Starting server on PORT: ${PORT}"

# Start the Flask application with gunicorn
# Using the gunicorn_config.py which binds to the PORT environment variable
exec gunicorn api_server:app --config gunicorn_config.py