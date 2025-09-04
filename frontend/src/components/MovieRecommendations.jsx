import React, { useState, useEffect } from 'react';
import { getMovieRecommendations, recordUserInteraction } from '../services/api';
import MovieCarousel from './MovieCarousel';

/**
 * MovieRecommendations component for displaying recommendations based on a selected movie
 * @param {Object} props - Component props
 * @param {Object} props.selectedMovie - The movie to get recommendations for
 * @param {Function} props.onMovieSelect - Function to call when a recommended movie is selected
 * @returns {JSX.Element} - Rendered component
 */
const MovieRecommendations = ({ selectedMovie, onMovieSelect }) => {
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!selectedMovie) return;

    const fetchRecommendations = async () => {
      try {
        setLoading(true);
        setError(null);
        
        // Record that user viewed this movie
        await recordUserInteraction(selectedMovie.movie_id, 'view');
        
        // Get personalized recommendations
        const data = await getMovieRecommendations(selectedMovie.title, true);
        setRecommendations(data);
      } catch (err) {
        console.error('Error fetching recommendations:', err);
        setError('Failed to load recommendations. Please try again.');
      } finally {
        setLoading(false);
      }
    };

    fetchRecommendations();
  }, [selectedMovie]);

  if (!selectedMovie) {
    return null;
  }

  return (
    <div className="mt-8">
      <h2 className="text-2xl font-bold mb-4">Because you liked "{selectedMovie.title}"</h2>
      
      {loading && (
        <div className="flex justify-center py-8">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary"></div>
        </div>
      )}
      
      {error && (
        <div className="text-destructive py-4">{error}</div>
      )}
      
      {!loading && !error && recommendations.length > 0 && (
        <MovieCarousel 
          movies={recommendations} 
          onMovieSelect={onMovieSelect} 
        />
      )}
      
      {!loading && !error && recommendations.length === 0 && (
        <div className="text-muted-foreground py-4">
          No recommendations found for this movie.
        </div>
      )}
    </div>
  );
};

export default MovieRecommendations;