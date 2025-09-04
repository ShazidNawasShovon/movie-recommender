/**
 * API service for connecting with the movie recommendation backend
 */

const API_URL = 'http://localhost:8502'; // Flask API port

// Get or create a user ID from localStorage
const getUserId = () => {
  let userId = localStorage.getItem('movie_recommender_user_id');
  return userId;
};

/**
 * Register a new user and store the user ID
 * @returns {Promise<string>} - The new user ID
 */
export const registerUser = async () => {
  try {
    // Send an empty body to avoid parsing issues
    const response = await fetch(`${API_URL}/user/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({})
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    localStorage.setItem('movie_recommender_user_id', data.user_id);
    return data.user_id;
  } catch (error) {
    console.error('Error registering user:', error);
    // Generate a fallback user ID if registration fails
    const fallbackUserId = `local-${Date.now()}`;
    localStorage.setItem('movie_recommender_user_id', fallbackUserId);
    return fallbackUserId;
  }
};

/**
 * Ensure user is registered, register if not
 * @returns {Promise<string>} - User ID
 */
export const ensureUserRegistered = async () => {
  const userId = getUserId();
  if (userId) return userId;
  return await registerUser();
};

/**
 * Fetch movie recommendations based on a selected movie
 * @param {string} movieName - The name of the movie to get recommendations for
 * @param {boolean} usePersonalization - Whether to use personalized recommendations
 * @returns {Promise<Array>} - Array of recommended movies
 */
export const getMovieRecommendations = async (movieName, usePersonalization = true) => {
  try {
    let userId = null;
    
    if (usePersonalization) {
      userId = await ensureUserRegistered();
    }
    
    const url = userId 
      ? `${API_URL}/recommend?movie_title=${encodeURIComponent(movieName)}&user_id=${userId}`
      : `${API_URL}/recommend?movie_title=${encodeURIComponent(movieName)}`;
      
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching movie recommendations:', error);
    throw error;
  }
};

/**
 * Fetch the list of all available movies with pagination
 * @param {number} page - Page number (default: 1)
 * @param {number} limit - Number of movies per page (default: 15)
 * @returns {Promise<Object>} - Object containing movies array and pagination info
 */
export const getAllMovies = async (page = 1, limit = 15) => {
  try {
    const response = await fetch(`${API_URL}/movies?page=${page}&limit=${limit}`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching all movies:', error);
    throw error;
  }
};

/**
 * Fetch all movies without pagination (for search functionality)
 * @returns {Promise<Array>} - Array of all movies
 */
export const getAllMoviesWithoutPagination = async () => {
  try {
    const response = await fetch(`${API_URL}/movies?limit=4800`); // Large limit to get all movies
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
    return data.movies;
  } catch (error) {
    console.error('Error fetching all movies:', error);
    throw error;
  }
};

/**
 * Search for movies by title
 * @param {string} query - The search query
 * @returns {Promise<Array>} - Array of matching movies
 */
export const searchMovies = async (query) => {
  try {
    if (!query || query.trim() === '') {
      return [];
    }
    
    console.log(`Searching for: ${query}`);
    
    // First try to use the backend search endpoint if available
    try {
      const response = await fetch(`${API_URL}/search?query=${encodeURIComponent(query.trim())}`);
      if (response.ok) {
        const data = await response.json();
        return data.movies || data;
      }
    } catch (searchError) {
      console.log('Backend search not available, falling back to client-side search');
      // Continue with client-side search if backend search fails
    }
    
    // Fallback: Get all movies and filter based on query
    const allMovies = await getAllMoviesWithoutPagination();
    return allMovies.filter(movie => 
      movie.title.toLowerCase().includes(query.toLowerCase())
    );
  } catch (error) {
    console.error('Error searching movies:', error);
    throw error;
  }
};

/**
 * Get personalized recommendations for the current user
 * @param {number} limit - Number of recommendations to return
 * @returns {Promise<Array>} - Array of recommended movies
 */
export const getUserRecommendations = async (limit = 10) => {
  try {
    const userId = await ensureUserRegistered();
    const response = await fetch(`${API_URL}/user/recommendations?user_id=${userId}&limit=${limit}`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching user recommendations:', error);
    throw error;
  }
};

/**
 * Record a user interaction with a movie
 * @param {string|number} movieId - The ID of the movie
 * @param {string} interactionType - Type of interaction (view, click, rate, watch)
 * @param {Object} details - Additional details about the interaction
 * @returns {Promise<Object>} - Response from the server
 */
export const recordUserInteraction = async (movieId, interactionType, details = {}) => {
  try {
    // Ensure we have a valid movie ID
    if (!movieId) {
      console.warn('Attempted to record interaction without a movie ID');
      return { success: false, error: 'Missing movie ID' };
    }
    
    const userId = await ensureUserRegistered();
    
    // Extract movie ID from movie object if needed
    const actualMovieId = typeof movieId === 'object' && movieId.id ? movieId.id : movieId;
    
    const payload = {
      user_id: userId,
      movie_id: actualMovieId,
      interaction_type: interactionType,
      ...details
    };
    
    console.log('Recording interaction:', payload);
    
    const response = await fetch(`${API_URL}/user/interact`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload)
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error recording user interaction:', error);
    // Don't throw the error to prevent disrupting the user experience
    return { success: false, error: error.message };
  }
};