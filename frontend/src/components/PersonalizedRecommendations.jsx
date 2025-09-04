import React, { useState, useEffect } from 'react';
import { getUserRecommendations } from '../services/api';
import MovieCarousel from './MovieCarousel';

/**
 * PersonalizedRecommendations component for displaying user-specific movie recommendations
 * @param {Object} props - Component props
 * @param {Function} props.onMovieSelect - Function to call when a movie is selected
 * @returns {JSX.Element} - Rendered component
 */
const PersonalizedRecommendations = ({ onMovieSelect }) => {
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchPersonalizedRecommendations = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await getUserRecommendations(10);
        setRecommendations(data);
      } catch (err) {
        console.error('Error fetching personalized recommendations:', err);
        setError('Unable to load personalized recommendations.');
      } finally {
        setLoading(false);
      }
    };

    fetchPersonalizedRecommendations();
  }, []);

  if (loading) {
    return (
      <div className="py-8">
        <h2 className="text-2xl font-bold mb-4">Recommended for You</h2>
        <div className="flex justify-center py-8">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary"></div>
        </div>
      </div>
    );
  }

  if (error || !recommendations || recommendations.length === 0) {
    return null; // Don't show anything if there are no personalized recommendations yet
  }

  return (
    <MovieCarousel 
      movies={recommendations} 
      title="Recommended for You"
      onMovieSelect={onMovieSelect} 
    />
  );
};

export default PersonalizedRecommendations;