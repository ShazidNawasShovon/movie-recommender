import os
import pickle
import pandas as pd
import json
import time
from sklearn.metrics.pairwise import cosine_similarity

class ModelUpdater:
    """
    A class to handle model updates for the movie recommendation system.
    This enables the system to learn from new user interactions and update the recommendation model.
    """
    
    def __init__(self, 
                 movies_path: str = "artifacts/movie_list.pkl",
                 similarity_path: str = "artifacts/similarity.pkl",
                 user_data_path: str = "data/user_interactions"):
        """
        Initialize the ModelUpdater.
        
        Args:
            movies_path: Path to the movie list pickle file
            similarity_path: Path to the similarity matrix pickle file
            user_data_path: Path to user interaction data directory
        """
        self.movies_path = movies_path
        self.similarity_path = similarity_path
        self.user_data_path = user_data_path
    
    def update_model_with_user_data(self):
        """
        Update the recommendation model using user interaction data.
        This enhances the content-based model with collaborative filtering elements.
        """
        if not os.path.exists(self.user_data_path):
            print(f"No user data found at {self.user_data_path}. Skipping model update.")
            return
        
        print("Updating model with user interaction data...")
        
        # Get all user directories
        user_dirs = [d for d in os.listdir(self.user_data_path) 
                    if os.path.isdir(os.path.join(self.user_data_path, d))]
        
        if not user_dirs:
            print("No user data found. Skipping model update.")
            return
        
        # Create user-movie interaction matrix
        user_movie_data = {}
        
        # Process each user's interaction data
        for user_id in user_dirs:
            user_dir = os.path.join(self.user_data_path, user_id)
            interaction_files = [os.path.join(user_dir, f) for f in os.listdir(user_dir) 
                                if f.endswith('.json')]
            
            # Process interaction files to build preference scores
            preferences = {}
            
            # Weight different interaction types
            weights = {
                "view": 1.0,
                "click": 2.0,
                "rate": 5.0,
                "watch": 3.0,
                "recommend": 0.5
            }
            
            # Calculate preference scores
            for file_path in interaction_files:
                try:
                    with open(file_path, 'r') as f:
                        interaction = json.load(f)
                    
                    movie_id = interaction.get("movie_id")
                    if not movie_id:
                        continue
                        
                    # Base score from interaction type
                    interaction_type = interaction.get("interaction_type", "view")
                    score = weights.get(interaction_type, 1.0)
                    
                    # Adjust score based on rating if available
                    if "rating" in interaction:
                        score *= interaction["rating"] / 2.5  # Normalize rating
                    
                    # Add to existing preference or create new entry
                    if movie_id in preferences:
                        preferences[movie_id] = (preferences[movie_id] + score) / 2
                    else:
                        preferences[movie_id] = score
                except Exception as e:
                    print(f"Error processing interaction file {file_path}: {e}")
            
            user_movie_data[user_id] = preferences
        
        # Convert to DataFrame for easier manipulation
        user_movie_df = pd.DataFrame(user_movie_data).T.fillna(0)
        
        # If we have enough users, calculate user similarity matrix
        if len(user_dirs) > 1 and not user_movie_df.empty:
            print("Calculating user similarity matrix...")
            user_similarity = cosine_similarity(user_movie_df.values)
            
            # Save user similarity matrix for collaborative filtering
            user_similarity_df = pd.DataFrame(
                user_similarity, 
                index=user_movie_df.index,
                columns=user_movie_df.index
            )
            
            # Save user-movie matrix and user similarity matrix
            os.makedirs("artifacts", exist_ok=True)
            pickle.dump(user_movie_df, open('artifacts/user_movie_matrix.pkl', 'wb'))
            pickle.dump(user_similarity_df, open('artifacts/user_similarity.pkl', 'wb'))
            
            print("User similarity matrix calculated and saved.")
        
        print("Model update completed.")
    
    def run_periodic_updates(self, interval_hours=24.0):
        """
        Run periodic model updates.
        
        Args:
            interval_hours: Time between updates in hours
        """
        while True:
            # Update the model
            self.update_model_with_user_data()
            
            # Sleep until next update
            print(f"Next update scheduled in {interval_hours} hours.")
            time.sleep(interval_hours * 3600)

# Example usage
if __name__ == "__main__":
    updater = ModelUpdater()
    updater.update_model_with_user_data()