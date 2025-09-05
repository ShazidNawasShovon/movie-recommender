from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
import pickle
import pandas as pd
import uuid
import os
import json
import requests

# Import custom modules
from src.utils.user_interactions import UserInteractionTracker
from src.models.hybrid_recommender import HybridRecommender

load_dotenv()
app = Flask(__name__)
# CORS(app, resources={r"/*": {"origins": ["https://movie-recommender-engine.netlify.app", "http://localhost:5173"]}})
# Enable CORS for all routes in development, or specific origins in production
if os.getenv("FLASK_ENV") == "development":
    CORS(app, resources={r"/*": {"origins": "*"}})
else:
    # In production, specify allowed origins
    allowed_origins = [
        "https://movie-recommender-engine.netlify.app",  # Main production frontend
        "http://localhost:5173"  # Local development frontend
    ]
    # Add custom origins from environment variable if provided
    custom_origin = os.getenv("ALLOWED_ORIGIN")
    if custom_origin:
        allowed_origins.append(custom_origin)
    
    CORS(app, resources={r"/*": {"origins": allowed_origins}})

# TMDB API Configuration
# NOTE: This is a sample key for demo purposes only. For production use, you must obtain your own API key
# from https://www.themoviedb.org/settings/api and agree to their terms of use.
# TMDB_API_KEY = "3fd2be6f0c70a2a598f084ddfb75487c"  # Replace with your own API key
TMDB_API_KEY = os.getenv("TMDB_API_KEY", "3fd2be6f0c70a2a598f084ddfb75487c")
TMDB_API_URL = os.getenv("TMDB_API_URL", "https://api.themoviedb.org/3")
TMDB_IMAGE_BASE_URL = os.getenv("TMDB_IMAGE_BASE_URL", "https://image.tmdb.org/t/p/")
TMDB_POSTER_SIZE = os.getenv("TMDB_POSTER_SIZE", "w500")
TMDB_BACKDROP_SIZE = os.getenv("TMDB_BACKDROP_SIZE", "w1280")

# Ensure user interaction directory exists
os.makedirs("data/user_interactions", exist_ok=True)

# Initialize user interaction tracker
user_tracker = UserInteractionTracker(storage_path="data/user_interactions")

# Initialize hybrid recommender
hybrid_recommender = HybridRecommender(
    movies_path="artifacts/movie_list.pkl",
    similarity_path="artifacts/similarity.pkl",
    user_data_path="data/user_interactions",
    content_weight=0.7,
    collaborative_weight=0.3
)

# Load movie data for direct access when needed
movies = pickle.load(open('artifacts/movie_list.pkl', 'rb'))

# Function to fetch movie details from TMDB API
def fetch_movie_details(movie_id):
    try:
        url = f"{TMDB_API_URL}/movie/{movie_id}?api_key={TMDB_API_KEY}"
        response = requests.get(url)
        if response.status_code == 200:
            movie_data = response.json()
            return {
                'poster_path': movie_data.get('poster_path'),
                'backdrop_path': movie_data.get('backdrop_path'),
                'original_title': movie_data.get('original_title')
            }
        else:
            print(f"Error fetching movie details: {response.status_code}")
            return None
    except Exception as e:
        print(f"Exception in fetch_movie_details: {e}")
        return None

# Function to recommend movies using the hybrid recommender
def recommend(movie, user_id=None):
    try:
        # Use the hybrid recommender to get recommendations
        recommendations = hybrid_recommender.get_recommendations(
            movie_title=movie,
            user_id=user_id,
            n=5
        )
        
        # If no recommendations were found, return empty list
        if not recommendations:
            return []
        
        # Enhance recommendations with TMDB data
        enhanced_recommendations = []
        for rec in recommendations:
            movie_id = rec['id']
            movie_details = fetch_movie_details(movie_id)
            
            poster_path = None
            backdrop_path = None
            
            if movie_details:
                poster_path = movie_details.get('poster_path')
                backdrop_path = movie_details.get('backdrop_path')
            
            enhanced_rec = {
                'id': movie_id,
                'title': rec['title'],
                'poster_url': f"{TMDB_IMAGE_BASE_URL}{TMDB_POSTER_SIZE}{poster_path}" if poster_path else None,
                'backdrop_url': f"{TMDB_IMAGE_BASE_URL}{TMDB_BACKDROP_SIZE}{backdrop_path}" if backdrop_path else None
            }
            enhanced_recommendations.append(enhanced_rec)
        
        return jsonify(enhanced_recommendations)
    except Exception as e:
        print(f"Error in recommend function: {e}")
        return []

@app.route('/')
def home():
    return "Movie Recommendation API"

@app.route('/search')
def search_movies():
    try:
        query = request.args.get('query', '').lower()
        if not query:
            return jsonify({'movies': [], 'error': 'No search query provided'}), 400
            
        # Filter movies by title
        filtered_movies = movies[movies['title'].str.contains(query, case=False)]
        
        search_results = []
        for _, row in filtered_movies.iterrows():
            movie_id = int(row['movie_id'])
            movie_details = fetch_movie_details(movie_id)
            
            poster_path = None
            backdrop_path = None
            
            if movie_details:
                poster_path = movie_details.get('poster_path')
                backdrop_path = movie_details.get('backdrop_path')
            
            search_results.append({
                'id': movie_id,
                'title': str(row['title']),
                'poster_url': f"{TMDB_IMAGE_BASE_URL}{TMDB_POSTER_SIZE}{poster_path}" if poster_path else None,
                'backdrop_url': f"{TMDB_IMAGE_BASE_URL}{TMDB_BACKDROP_SIZE}{backdrop_path}" if backdrop_path else None
            })
            
            # Limit to 50 results for performance
            if len(search_results) >= 50:
                break
        
        return jsonify({'movies': search_results})
    except Exception as e:
        print(f"Error in search_movies: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/movies')
def get_movies():
    try:
        # Get pagination parameters
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 15))
        
        # Calculate offset
        offset = (page - 1) * limit
        
        movie_data = []
        for _, row in movies.iloc[offset:offset + limit].iterrows():
            movie_id = int(row['movie_id'])
            movie_details = fetch_movie_details(movie_id)
            
            poster_path = None
            backdrop_path = None
            
            if movie_details:
                poster_path = movie_details.get('poster_path')
                backdrop_path = movie_details.get('backdrop_path')
            
            movie_data.append({
                'id': movie_id,
                'title': str(row['title']),
                'poster_url': f"{TMDB_IMAGE_BASE_URL}{TMDB_POSTER_SIZE}{poster_path}" if poster_path else None,
                'backdrop_url': f"{TMDB_IMAGE_BASE_URL}{TMDB_BACKDROP_SIZE}{backdrop_path}" if backdrop_path else None
            })
        
        # Return pagination info
        total_movies = len(movies)
        total_pages = (total_movies + limit - 1) // limit
        
        return jsonify({
            'movies': movie_data,
            'pagination': {
                'page': page,
                'limit': limit,
                'total': total_movies,
                'total_pages': total_pages,
                'has_next': page < total_pages,
                'has_prev': page > 1
            }
        })
    except Exception as e:
        print(f"Error in get_movies: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/recommend')
def get_recommendations():
    try:
        movie_title = request.args.get('movie_title')
        user_id = request.args.get('user_id')
        
        if not movie_title and not user_id:
            return jsonify({"error": "Either movie_title or user_id parameter is required"}), 400
        
        # Record view interaction if user_id is provided
        if user_id and movie_title:
            # Find movie_id from title
            movie_matches = movies[movies['title'] == movie_title]
            if len(movie_matches) > 0:
                movie_id = int(movie_matches.iloc[0]['movie_id'])
                user_tracker.record_interaction(
                    user_id=user_id,
                    movie_id=movie_id,
                    interaction_type="view"
                )
        
        recommendations = recommend(movie_title, user_id)
        if not recommendations:
            return jsonify({"error": "Movie not found or no recommendations available"}), 404
        
        return jsonify(recommendations)
    except Exception as e:
        print(f"Error in get_recommendations: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/user/interact', methods=['POST', 'OPTIONS'])
def record_user_interaction():
    # Handle CORS preflight request
    if request.method == 'OPTIONS':
        return '', 200
        
    try:
        # Parse data from different request formats
        data = {}
        if request.is_json:
            data = request.json or {}
        elif request.form:
            data = request.form.to_dict() or {}
        elif request.data:
            try:
                data = json.loads(request.data) or {}
            except:
                # If we can't parse JSON, just use empty dict
                pass
        
        # Validate required fields
        required_fields = ['user_id', 'movie_id', 'interaction_type']
        missing_fields = [field for field in required_fields if not data.get(field)]
        
        if missing_fields:
            return jsonify({"error": f"Missing required field: {missing_fields[0]}", "missing_fields": missing_fields}), 400
        
        # Convert movie_id to int if it's a string
        try:
            if isinstance(data['movie_id'], str) and data['movie_id'].isdigit():
                data['movie_id'] = int(data['movie_id'])
        except (ValueError, TypeError):
            pass  # Keep as is if conversion fails
        
        # Record the interaction
        success = user_tracker.record_interaction(
            user_id=data['user_id'],
            movie_id=data['movie_id'],
            interaction_type=data['interaction_type'],
            rating=data.get('rating'),
            watch_duration=data.get('watch_duration')
        )
        
        if not success:
            return jsonify({"error": "Failed to record interaction"}), 500
        
        # If this is a rating or watch interaction, update the model
        if data['interaction_type'] in ['rate', 'watch']:
            hybrid_recommender.update_model()
        
        return jsonify({"success": True})
    except Exception as e:
        print(f"Error in record_user_interaction: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/user/recommendations')
def get_user_recommendations():
    try:
        user_id = request.args.get('user_id')
        if not user_id:
            return jsonify({"error": "user_id parameter is missing"}), 400
            
        # Get limit parameter with default of 10
        try:
            limit = int(request.args.get('limit', 10))
        except ValueError:
            limit = 10
        
        # Get personalized recommendations for the user
        recommendations = hybrid_recommender.get_recommendations(
            user_id=user_id,
            n=limit
        )
        
        if not recommendations:
            # If no personalized recommendations, return some popular movies
            popular_movies = movies.head(limit).to_dict('records')
            return jsonify(popular_movies)
        
        # Record these recommendations
        for rec in recommendations:
            user_tracker.record_interaction(
                user_id=user_id,
                movie_id=rec['id'],
                interaction_type="recommend"
            )
        
        return jsonify(recommendations)
    except Exception as e:
        print(f"Error in get_user_recommendations: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/user/register', methods=['POST', 'OPTIONS'])
def register_user():
    # Handle CORS preflight request
    if request.method == 'OPTIONS':
        return '', 200
        
    try:
        # Generate a new user ID if one isn't provided
        # Handle different request formats
        data = {}
        if request.is_json:
            data = request.json or {}
        elif request.form:
            data = request.form.to_dict() or {}
        elif request.data:
            try:
                data = json.loads(request.data) or {}
            except:
                # If we can't parse JSON, just use empty dict
                pass
            
        # If no data was provided, create an empty user
        user_id = data.get('user_id', str(uuid.uuid4()))
        
        # Create user directory
        user_dir = os.path.join("data/user_interactions", user_id)
        os.makedirs(user_dir, exist_ok=True)
        
        print(f"Successfully registered user: {user_id}")
        return jsonify({
            "user_id": user_id,
            "success": True
        })
    except Exception as e:
        print(f"Error in register_user: {e}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

# Print port binding information at module level to ensure it's visible when imported by Gunicorn
port = int(os.getenv("PORT", 5000))
print(f"Flask app configured to bind to port: {port}")

if __name__ == "__main__":
    # This block only runs when the script is executed directly (not through Gunicorn)
    app.run(host="0.0.0.0", port=port or 5000)
