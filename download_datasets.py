import os
import requests
import zipfile
import io

def download_datasets():
    """
    Download the TMDB 5000 movie and credits datasets required for model training.
    """
    print("Downloading TMDB 5000 datasets...")
    
    # Create data directory if it doesn't exist
    os.makedirs("data", exist_ok=True)
    
    # URLs for the datasets
    movies_url = "https://raw.githubusercontent.com/ShazidNawasShovon/Movie-Recommender/main/data/tmdb_5000_movies.csv"
    credits_url = "https://raw.githubusercontent.com/ShazidNawasShovon/Movie-Recommender/main/data/tmdb_5000_credits.csv"
    
    # Download movies dataset
    try:
        print("Downloading movies dataset...")
        response = requests.get(movies_url)
        response.raise_for_status()
        
        with open("data/tmdb_5000_movies.csv", "wb") as f:
            f.write(response.content)
        print("Movies dataset downloaded successfully.")
    except Exception as e:
        print(f"Error downloading movies dataset: {e}")
        return False
    
    # Download credits dataset
    try:
        print("Downloading credits dataset...")
        response = requests.get(credits_url)
        response.raise_for_status()
        
        with open("data/tmdb_5000_credits.csv", "wb") as f:
            f.write(response.content)
        print("Credits dataset downloaded successfully.")
    except Exception as e:
        print(f"Error downloading credits dataset: {e}")
        return False
    
    print("All datasets downloaded successfully.")
    return True

if __name__ == "__main__":
    download_datasets()