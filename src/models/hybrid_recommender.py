import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
import pickle
import os
from sklearn.metrics.pairwise import cosine_similarity

class HybridRecommender:
    """
    A hybrid recommendation system that combines content-based filtering and collaborative filtering
    to provide more personalized movie recommendations.
    
    This system improves upon the basic content-based approach by incorporating user preferences
    and interaction data to deliver more relevant recommendations similar to commercial systems.
    """
    
    def __init__(self, 
                 movies_path: str = "artifacts/movie_list.pkl",
                 similarity_path: str = "artifacts/similarity.pkl",
                 user_data_path: str = "data/user_interactions",
                 content_weight: float = 0.7,
                 collaborative_weight: float = 0.3):
        """
        Initialize the hybrid recommender system.
        
        Args:
            movies_path: Path to the movie list pickle file
            similarity_path: Path to the content similarity matrix pickle file
            user_data_path: Path to user interaction data directory
            content_weight: Weight for content-based recommendations (0-1)
            collaborative_weight: Weight for collaborative filtering recommendations (0-1)
        """
        # Load movie data and content-based similarity matrix
        self.movies = pickle.load(open(movies_path, 'rb'))
        self.content_similarity = pickle.load(open(similarity_path, 'rb'))
        
        # Set weights for hybrid approach
        self.content_weight = content_weight
        self.collaborative_weight = collaborative_weight
        
        # Path to user interaction data
        self.user_data_path = user_data_path
        
        # Cache for user similarity matrix (will be built on demand)
        self._user_similarity_matrix = None
        self._user_movie_matrix = None
        self._user_ids = []
        
        # Initialize user-item matrix when needed
        self._initialize_user_matrices()
    
    def _initialize_user_matrices(self) -> None:
        """
        Initialize user-item matrix from stored user interactions.
        This builds the foundation for collaborative filtering.
        """
        if not os.path.exists(self.user_data_path):
            # No user data yet, will initialize later when data is available
            return
        
        # Get all user IDs from the user data directory
        user_dirs = [d for d in os.listdir(self.user_data_path) 
                    if os.path.isdir(os.path.join(self.user_data_path, d))]
        
        if not user_dirs:
            return
            
        self._user_ids = user_dirs
        
        # Create user-movie matrix (users as rows, movies as columns)
        # This will be a sparse matrix where each cell represents a user's preference for a movie
        user_movie_data = {}
        
        # Process each user's interaction data
        for user_id in self._user_ids:
            # Get user's movie preferences
            user_prefs = self._get_user_preferences(user_id)
            user_movie_data[user_id] = user_prefs
        
        # Convert to DataFrame for easier manipulation
        self._user_movie_matrix = pd.DataFrame(user_movie_data).T.fillna(0)
        
        # Calculate user similarity matrix if we have enough users
        if len(self._user_ids) > 1:
            self._calculate_user_similarity()
    
    def _get_user_preferences(self, user_id: str) -> Dict[int, float]:
        """
        Get a user's movie preferences from their interaction data.
        
        Args:
            user_id: The user ID to get preferences for
            
        Returns:
            Dictionary mapping movie_id to preference score
        """
        user_dir = os.path.join(self.user_data_path, user_id)
        if not os.path.exists(user_dir):
            return {}
        
        # Get all interaction files for this user
        interaction_files = [os.path.join(user_dir, f) for f in os.listdir(user_dir) 
                            if f.endswith('.json')]
        
        import json
        
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
                
                # Adjust score based on watch duration if available
                if "watch_duration" in interaction:
                    # Longer watch times indicate higher interest
                    duration_factor = min(interaction["watch_duration"] / 3600, 2.0)
                    score *= (1.0 + duration_factor / 2.0)
                
                # Add to existing preference or create new entry
                if movie_id in preferences:
                    preferences[movie_id] = (preferences[movie_id] + score) / 2
                else:
                    preferences[movie_id] = score
            except Exception as e:
                print(f"Error processing interaction file {file_path}: {e}")
        
        return preferences
    
    def _calculate_user_similarity(self) -> None:
        """
        Calculate similarity between users based on their movie preferences.
        """
        if self._user_movie_matrix is None or self._user_movie_matrix.empty:
            return
            
        # Calculate cosine similarity between users
        user_similarity = cosine_similarity(self._user_movie_matrix.values)
        self._user_similarity_matrix = pd.DataFrame(
            user_similarity, 
            index=self._user_movie_matrix.index,
            columns=self._user_movie_matrix.index
        )
    
    def _get_content_based_recommendations(self, movie_title: str, n: int = 10) -> List[Dict]:
        """
        Get content-based recommendations for a movie.
        
        Args:
            movie_title: Title of the movie to get recommendations for
            n: Number of recommendations to return
            
        Returns:
            List of recommended movies with details
        """
        try:
            # Find the movie index
            movie_matches = self.movies[self.movies['title'] == movie_title]
            if len(movie_matches) == 0:
                return []
            
            index = movie_matches.index[0]
            distances = sorted(list(enumerate(self.content_similarity[index])), 
                              reverse=True, key=lambda x: x[1])
            
            recommended_movies = []
            for i in distances[1:n+1]:  # Skip the first one as it's the movie itself
                movie_row = self.movies.iloc[i[0]]
                recommended_movies.append({
                    'id': int(movie_row['movie_id']),
                    'title': str(movie_row['title']),
                    'poster_url': f"https://image.tmdb.org/t/p/w500/{int(movie_row['movie_id'])}.jpg",
                    'similarity_score': float(i[1])
                })
            return recommended_movies
        except Exception as e:
            print(f"Error in content-based recommendations: {e}")
            return []
    
    def _get_collaborative_recommendations(self, user_id: str, n: int = 10) -> List[Dict]:
        """
        Get collaborative filtering recommendations for a user.
        
        Args:
            user_id: ID of the user to get recommendations for
            n: Number of recommendations to return
            
        Returns:
            List of recommended movies with details
        """
        if user_id not in self._user_ids or self._user_similarity_matrix is None:
            return []
        
        try:
            # Get similar users
            similar_users = self._user_similarity_matrix[user_id].sort_values(ascending=False)[1:11]  # Top 10 similar users
            
            # Get movies liked by similar users that the current user hasn't interacted with
            user_prefs = self._get_user_preferences(user_id)
            user_movies = set(user_prefs.keys())
            
            # Collect recommendations from similar users
            recommendations = {}
            
            for sim_user, similarity in similar_users.items():
                sim_user_prefs = self._get_user_preferences(sim_user)
                
                for movie_id, score in sim_user_prefs.items():
                    # Skip movies the user has already interacted with
                    if movie_id in user_movies:
                        continue
                    
                    # Weight the recommendation by user similarity
                    weighted_score = score * similarity
                    
                    if movie_id in recommendations:
                        recommendations[movie_id] += weighted_score
                    else:
                        recommendations[movie_id] = weighted_score
            
            # Sort recommendations by score
            sorted_recommendations = sorted(recommendations.items(), 
                                           key=lambda x: x[1], reverse=True)[:n]
            
            # Format recommendations
            recommended_movies = []
            for movie_id, score in sorted_recommendations:
                # Find movie details
                movie_matches = self.movies[self.movies['movie_id'] == movie_id]
                if len(movie_matches) == 0:
                    continue
                    
                movie_row = movie_matches.iloc[0]
                recommended_movies.append({
                    'id': int(movie_id),
                    'title': str(movie_row['title']),
                    'poster_url': f"https://image.tmdb.org/t/p/w500/{int(movie_id)}.jpg",
                    'similarity_score': float(score)
                })
            
            return recommended_movies
        except Exception as e:
            print(f"Error in collaborative recommendations: {e}")
            return []
    
    def get_recommendations(self, movie_title: str = None, user_id: str = None, n: int = 5) -> List[Dict]:
        """
        Get hybrid recommendations based on movie title and/or user ID.
        
        Args:
            movie_title: Optional title of the movie to get recommendations for
            user_id: Optional ID of the user to get recommendations for
            n: Number of recommendations to return
            
        Returns:
            List of recommended movies with details
        """
        # Refresh user matrices to ensure we have the latest data
        self._initialize_user_matrices()
        
        # Get content-based recommendations if movie title is provided
        content_recs = []
        if movie_title:
            content_recs = self._get_content_based_recommendations(movie_title, n=n*2)
        
        # Get collaborative recommendations if user ID is provided
        collab_recs = []
        if user_id and user_id in self._user_ids:
            collab_recs = self._get_collaborative_recommendations(user_id, n=n*2)
        
        # If we only have one type of recommendations, return those
        if not content_recs:
            return collab_recs[:n]
        if not collab_recs:
            return content_recs[:n]
        
        # Combine recommendations with weights
        # Create dictionaries for easier lookup
        content_dict = {rec['id']: rec for rec in content_recs}
        collab_dict = {rec['id']: rec for rec in collab_recs}
        
        # Combine unique movie IDs from both recommendation sets
        all_movie_ids = set(content_dict.keys()) | set(collab_dict.keys())
        
        # Calculate hybrid scores
        hybrid_scores = {}
        for movie_id in all_movie_ids:
            content_score = content_dict.get(movie_id, {}).get('similarity_score', 0)
            collab_score = collab_dict.get(movie_id, {}).get('similarity_score', 0)
            
            # Calculate weighted hybrid score
            hybrid_scores[movie_id] = (
                self.content_weight * content_score + 
                self.collaborative_weight * collab_score
            )
        
        # Sort by hybrid score and take top n
        top_movies = sorted(hybrid_scores.items(), key=lambda x: x[1], reverse=True)[:n]
        
        # Format final recommendations
        recommendations = []
        for movie_id, score in top_movies:
            # Prefer content dict for movie details as it's more likely to have them
            movie_data = content_dict.get(movie_id) or collab_dict.get(movie_id)
            if movie_data:
                movie_data['similarity_score'] = score  # Update with hybrid score
                recommendations.append(movie_data)
        
        return recommendations
    
    def update_model(self) -> None:
        """
        Update the recommendation model with new user interaction data.
        This should be called periodically to refresh the collaborative filtering component.
        """
        self._initialize_user_matrices()