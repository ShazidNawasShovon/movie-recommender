import json
import os
import time
from datetime import datetime
from typing import Dict, List, Optional, Union

class UserInteractionTracker:
    """
    A class to track and store user interactions with movies for personalized recommendations.
    This enables the system to learn from user behavior and improve recommendations over time.
    """
    
    def __init__(self, storage_path: str = "data/user_interactions"):
        """
        Initialize the UserInteractionTracker.
        
        Args:
            storage_path: Directory path to store user interaction data
        """
        self.storage_path = storage_path
        os.makedirs(storage_path, exist_ok=True)
    
    def record_interaction(self, 
                          user_id: str, 
                          movie_id: int, 
                          interaction_type: str, 
                          rating: Optional[float] = None,
                          watch_duration: Optional[int] = None,
                          timestamp: Optional[float] = None) -> bool:
        """
        Record a user interaction with a movie.
        
        Args:
            user_id: Unique identifier for the user
            movie_id: ID of the movie the user interacted with
            interaction_type: Type of interaction (view, click, rate, watch, recommend)
            rating: Optional rating given by user (1-5)
            watch_duration: Optional duration watched in seconds
            timestamp: Optional timestamp of interaction (defaults to current time)
            
        Returns:
            bool: True if interaction was recorded successfully
        """
        if timestamp is None:
            timestamp = time.time()
            
        interaction = {
            "user_id": user_id,
            "movie_id": movie_id,
            "interaction_type": interaction_type,
            "timestamp": timestamp,
            "datetime": datetime.fromtimestamp(timestamp).isoformat()
        }
        
        if rating is not None:
            interaction["rating"] = max(min(float(rating), 5.0), 1.0)  # Ensure rating is between 1-5
            
        if watch_duration is not None:
            interaction["watch_duration"] = max(0, int(watch_duration))  # Ensure duration is positive
        
        # Create user-specific directory if it doesn't exist
        user_dir = os.path.join(self.storage_path, user_id)
        os.makedirs(user_dir, exist_ok=True)
        
        # Save interaction to user's interaction log
        interaction_file = os.path.join(user_dir, f"{int(timestamp)}.json")
        try:
            with open(interaction_file, 'w') as f:
                json.dump(interaction, f)
            return True
        except Exception as e:
            print(f"Error recording interaction: {e}")
            return False
    
    def get_user_interactions(self, user_id: str, limit: int = 100, 
                             interaction_types: Optional[List[str]] = None) -> List[Dict]:
        """
        Get a user's recent interactions.
        
        Args:
            user_id: Unique identifier for the user
            limit: Maximum number of interactions to return
            interaction_types: Optional filter for specific interaction types
            
        Returns:
            List of interaction records
        """
        user_dir = os.path.join(self.storage_path, user_id)
        if not os.path.exists(user_dir):
            return []
        
        interaction_files = sorted(
            [os.path.join(user_dir, f) for f in os.listdir(user_dir) if f.endswith('.json')],
            reverse=True
        )[:limit]
        
        interactions = []
        for file_path in interaction_files:
            try:
                with open(file_path, 'r') as f:
                    interaction = json.load(f)
                    
                if interaction_types and interaction.get("interaction_type") not in interaction_types:
                    continue
                    
                interactions.append(interaction)
            except Exception as e:
                print(f"Error reading interaction file {file_path}: {e}")
        
        return interactions
    
    def get_user_movie_preferences(self, user_id: str) -> Dict[int, float]:
        """
        Calculate user's movie preferences based on their interactions.
        
        Args:
            user_id: Unique identifier for the user
            
        Returns:
            Dictionary mapping movie_id to preference score
        """
        interactions = self.get_user_interactions(user_id, limit=1000)
        
        # Initialize preference scores
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
        for interaction in interactions:
            movie_id = interaction.get("movie_id")
            if not movie_id:
                continue
                
            # Base score from interaction type
            interaction_type = interaction.get("interaction_type", "view")
            score = weights.get(interaction_type, 1.0)
            
            # Adjust score based on rating if available
            if "rating" in interaction:
                score *= interaction["rating"] / 2.5  # Normalize rating to scale the score
            
            # Adjust score based on watch duration if available
            if "watch_duration" in interaction:
                # Longer watch times indicate higher interest, up to a point
                duration_factor = min(interaction["watch_duration"] / 3600, 2.0)  # Cap at 2x for 1+ hour
                score *= (1.0 + duration_factor / 2.0)
            
            # Add to existing preference or create new entry
            if movie_id in preferences:
                preferences[movie_id] = (preferences[movie_id] + score) / 2  # Average with existing score
            else:
                preferences[movie_id] = score
        
        return preferences