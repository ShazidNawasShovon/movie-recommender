import os
import pickle
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.stem.porter import PorterStemmer
import requests
import ast

class ModelTrainer:
    """
    A class to handle model training for the movie recommendation system.
    This includes initial content-based model training and updates.
    """
    
    def __init__(self, 
                 movies_path: str = "artifacts/movie_list.pkl",
                 similarity_path: str = "artifacts/similarity.pkl",
                 tmdb_api_key: str = None):
        """
        Initialize the ModelTrainer.
        
        Args:
            movies_path: Path to save the movie list pickle file
            similarity_path: Path to save the similarity matrix pickle file
            tmdb_api_key: API key for The Movie Database (optional)
        """
        self.movies_path = movies_path
        self.similarity_path = similarity_path
        self.tmdb_api_key = tmdb_api_key or os.environ.get('TMDB_API_KEY')
        
        # Create artifacts directory if it doesn't exist
        os.makedirs(os.path.dirname(movies_path), exist_ok=True)
        
        # Initialize NLTK resources
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')
        
        self.ps = PorterStemmer()
    
    def stem(self, text):
        """
        Apply stemming to text.
        
        Args:
            text: Text to stem
            
        Returns:
            Stemmed text
        """
        y = []
        for i in text.split():
            y.append(self.ps.stem(i))
        return " ".join(y)
    
    def convert_list_string(self, obj):
        """
        Convert string representation of list to actual list.
        
        Args:
            obj: String representation of list or actual list
            
        Returns:
            List of strings
        """
        if isinstance(obj, str):
            try:
                return ast.literal_eval(obj)
            except:
                return []
        return obj if isinstance(obj, list) else []
    
    def fetch_poster_path(self, movie_id):
        """
        Fetch movie poster path from TMDB API.
        
        Args:
            movie_id: TMDB movie ID
            
        Returns:
            Poster path or None if not found
        """
        if not self.tmdb_api_key:
            return None
            
        try:
            response = requests.get(
                f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={self.tmdb_api_key}&language=en-US'
            )
            data = response.json()
            return data.get('poster_path')
        except Exception as e:
            print(f"Error fetching poster for movie {movie_id}: {e}")
            return None
    
    def train_content_based_model(self, movies_csv="data/tmdb_5000_movies.csv", credits_csv="data/tmdb_5000_credits.csv"):
        """
        Train the content-based recommendation model.
        
        Args:
            movies_csv: Path to movies CSV file
            credits_csv: Path to credits CSV file
            
        Returns:
            Tuple of (movies DataFrame, similarity matrix)
        """
        print("Loading movie datasets...")
        try:
            movies = pd.read_csv(movies_csv)
            credits = pd.read_csv(credits_csv)
        except Exception as e:
            print(f"Error loading datasets: {e}")
            return None, None
        
        print("Processing movie data...")
        # Merge datasets
        movies = movies.merge(credits, on='title')
        
        # Select relevant features
        movies = movies[['id', 'title', 'overview', 'genres', 'keywords', 'cast', 'crew']]
        
        # Drop rows with missing values
        movies.dropna(inplace=True)
        
        # Process string representations of lists
        for feature in ['genres', 'keywords', 'cast', 'crew']:
            movies[feature] = movies[feature].apply(self.convert_list_string)
        
        # Extract director from crew
        movies['director'] = movies['crew'].apply(lambda x: [i['name'] for i in x if i['job'] == 'Director'])
        
        # Extract top 3 cast members
        movies['cast'] = movies['cast'].apply(lambda x: [i['name'] for i in x][:3])
        
        # Extract genre names
        movies['genres'] = movies['genres'].apply(lambda x: [i['name'] for i in x])
        
        # Extract keyword names
        movies['keywords'] = movies['keywords'].apply(lambda x: [i['name'] for i in x])
        
        # Convert overview to list for consistency
        movies['overview'] = movies['overview'].apply(lambda x: x.split())
        
        # Remove spaces from names
        for feature in ['cast', 'director', 'genres', 'keywords']:
            movies[feature] = movies[feature].apply(lambda x: [i.replace(" ", "") for i in x])
        
        # Create tags by combining features
        movies['tags'] = movies['overview'] + movies['genres'] + movies['keywords'] + movies['cast'] + movies['director']
        
        # Create a new DataFrame with selected columns
        new_df = movies[['id', 'title', 'tags']]
        
        # Convert tags to string
        new_df['tags'] = new_df['tags'].apply(lambda x: " ".join(x).lower())
        
        # Apply stemming to tags
        print("Applying stemming to tags...")
        new_df['tags'] = new_df['tags'].apply(self.stem)
        
        # Create count vectors
        print("Creating count vectors...")
        cv = CountVectorizer(max_features=5000, stop_words='english')
        vectors = cv.fit_transform(new_df['tags']).toarray()
        
        # Calculate cosine similarity
        print("Calculating cosine similarity...")
        similarity = cosine_similarity(vectors)
        
        # Rename id to movie_id for clarity
        new_df.rename(columns={'id': 'movie_id'}, inplace=True)
        
        # Add poster paths if API key is available
        if self.tmdb_api_key:
            print("Fetching poster paths...")
            new_df['poster_path'] = new_df['movie_id'].apply(self.fetch_poster_path)
        
        # Save processed data
        print(f"Saving model to {self.movies_path} and {self.similarity_path}...")
        pickle.dump(new_df, open(self.movies_path, 'wb'))
        pickle.dump(similarity, open(self.similarity_path, 'wb'))
        
        print("Content-based model training completed.")
        return new_df, similarity

# Example usage
if __name__ == "__main__":
    trainer = ModelTrainer()
    trainer.train_content_based_model()