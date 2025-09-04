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

# Start the Flask application with gunicorn
# Make sure to bind to the PORT environment variable provided by Render
exec gunicorn api_server:app --config gunicorn_config.py