from dotenv import load_dotenv
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
load_dotenv()
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
        self.tmdb_api_key = tmdb_api_key or os.getenv('TMDB_API_KEY')
        
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
            # Use low_memory=False to avoid mixed type inference issues
            # Use dtype specification for optimization
            dtype_dict = {
                'id': 'int32',
                'title': 'str',
                'overview': 'str'
            }
            movies = pd.read_csv(movies_csv, low_memory=False, dtype=dtype_dict)
            credits = pd.read_csv(credits_csv, low_memory=False, dtype=dtype_dict)
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
        # Use copy=True to avoid SettingWithCopyWarning
        new_df = movies[['id', 'title', 'tags']].copy()
        
        # Convert tags to string - use .loc to avoid SettingWithCopyWarning
        print("Converting tags to string...")
        new_df.loc[:, 'tags'] = new_df['tags'].apply(lambda x: " ".join(x).lower())
        
        # Apply stemming to tags - use .loc to avoid SettingWithCopyWarning
        print("Applying stemming to tags...")
        new_df.loc[:, 'tags'] = new_df['tags'].apply(self.stem)
        
        # Free up memory
        movies = None
        credits = None
        import gc
        gc.collect()
        
        # Create count vectors with reduced memory usage
        print("Creating count vectors...")
        cv = CountVectorizer(max_features=3000, stop_words='english')
        vectors = cv.fit_transform(new_df['tags'])  # Keep as sparse matrix, don't convert to array
        
        # Calculate cosine similarity in chunks to reduce memory usage
        print("Calculating cosine similarity...")
        # Use a smaller chunk size for lower memory usage
        chunk_size = 1000
        n_samples = vectors.shape[0]
        similarity = np.zeros((n_samples, n_samples), dtype=np.float32)  # Use float32 instead of float64
        
        for i in range(0, n_samples, chunk_size):
            end = min(i + chunk_size, n_samples)
            chunk = vectors[i:end]
            similarity[i:end] = cosine_similarity(chunk, vectors)
            # Free memory after each chunk
            if i % (chunk_size * 2) == 0:
                print(f"Processed {i}/{n_samples} samples...")
                gc.collect()
        
        # Rename id to movie_id for clarity
        new_df.rename(columns={'id': 'movie_id'}, inplace=True)
        
        # Add poster paths if API key is available
        if self.tmdb_api_key:
            print("Fetching poster paths...")
            new_df['poster_path'] = new_df['movie_id'].apply(self.fetch_poster_path)
        
        # Save processed data
        print(f"Saving model to {self.movies_path} and {self.similarity_path}...")
        # Save in chunks to reduce memory usage
        with open(self.movies_path, 'wb') as f:
            pickle.dump(new_df, f, protocol=4)
        
        with open(self.similarity_path, 'wb') as f:
            pickle.dump(similarity, f, protocol=4)
        
        print("Content-based model training completed.")
        return new_df, similarity

# Example usage
if __name__ == "__main__":
    trainer = ModelTrainer()
    trainer.train_content_based_model()