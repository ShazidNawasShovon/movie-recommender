import os
import sys
import time
import argparse
import threading

# Add the project root to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.models.model_updater import ModelUpdater
from src.models.model_trainer import ModelTrainer

def parse_arguments():
    """
    Parse command line arguments.
    """
    parser = argparse.ArgumentParser(description='Movie Recommendation Model Retraining Script')
    parser.add_argument('--interval', type=float, default=24.0,
                        help='Interval between model updates in hours (default: 24.0)')
    parser.add_argument('--initial-train', action='store_true',
                        help='Run initial model training before starting update loop')
    parser.add_argument('--movies-path', type=str, default='artifacts/movie_list.pkl',
                        help='Path to the movie list pickle file')
    parser.add_argument('--similarity-path', type=str, default='artifacts/similarity.pkl',
                        help='Path to the similarity matrix pickle file')
    parser.add_argument('--user-data-path', type=str, default='data/user_interactions',
                        help='Path to user interaction data directory')
    return parser.parse_args()

def run_model_updates(interval_hours, movies_path, similarity_path, user_data_path):
    """
    Run periodic model updates.
    
    Args:
        interval_hours: Time between updates in hours
        movies_path: Path to the movie list pickle file
        similarity_path: Path to the similarity matrix pickle file
        user_data_path: Path to user interaction data directory
    """
    updater = ModelUpdater(
        movies_path=movies_path,
        similarity_path=similarity_path,
        user_data_path=user_data_path
    )
    
    print(f"Starting model update loop with {interval_hours} hour interval")
    
    while True:
        try:
            # Update the model
            updater.update_model_with_user_data()
            
            # Sleep until next update
            print(f"Next update scheduled in {interval_hours} hours.")
            time.sleep(interval_hours * 3600)
        except KeyboardInterrupt:
            print("Model update loop interrupted. Exiting...")
            break
        except Exception as e:
            print(f"Error in model update loop: {e}")
            print("Retrying in 1 hour...")
            time.sleep(3600)

def main():
    """
    Main function to run the model retraining script.
    """
    args = parse_arguments()
    
    # Run initial model training if requested
    if args.initial_train:
        print("Running initial model training...")
        trainer = ModelTrainer()
        trainer.train_content_based_model()
        print("Initial model training completed.")
    
    # Start model update loop in a separate thread
    update_thread = threading.Thread(
        target=run_model_updates,
        args=(
            args.interval,
            args.movies_path,
            args.similarity_path,
            args.user_data_path
        ),
        daemon=True
    )
    update_thread.start()
    
    try:
        # Keep the main thread alive
        while update_thread.is_alive():
            time.sleep(1)
    except KeyboardInterrupt:
        print("Script interrupted. Exiting...")
        sys.exit(0)

if __name__ == "__main__":
    main()