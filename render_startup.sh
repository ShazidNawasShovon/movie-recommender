#!/bin/bash

# Set environment variables for production
export FLASK_ENV="production"

# Check if model files exist
if [ ! -f "artifacts/movie_list.pkl" ] || [ ! -f "artifacts/similarity.pkl" ]; then
    echo "Model files not found. Running initial training..."
    # Create artifacts directory if it doesn't exist
    mkdir -p artifacts
    # Download datasets if needed
    python download_datasets.py
    # Run initial model training
    python src/scripts/retrain_model.py --initial-train
    echo "Initial training completed."
fi

# Create data/user_interactions directory if it doesn't exist
mkdir -p data/user_interactions

# Start the Flask application with gunicorn
exec gunicorn api_server:app