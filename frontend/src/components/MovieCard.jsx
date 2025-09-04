import React, { useState } from 'react';
import { Card, CardContent } from './ui/card';
import { recordUserInteraction } from '../services/api';

/**
 * MovieCard component for displaying a movie with its poster and title
 * @param {Object} props - Component props
 * @param {Object} props.movie - Movie data object
 * @param {Function} props.onClick - Click handler function
 * @returns {JSX.Element} - Rendered component
 */
const MovieCard = ({ movie, onClick }) => {
  // Fix TMDB image URL format
  const getProperImageUrl = (movie) => {
    // If poster_url is null or contains undefined, use placeholder
    if (!movie.poster_url || movie.poster_url.includes('undefined') || movie.poster_url === 'null') {
      return `https://placehold.co/300x450/1f2937/ffffff?text=${encodeURIComponent(movie.title)}`;
    }
    
    // The API now returns complete URLs from TMDB API
    // Just return the poster_url directly
    return movie.poster_url;
  };
  
  const [imgSrc, setImgSrc] = useState(getProperImageUrl(movie));
  
  const handleImageError = () => {
    setImgSrc(`https://placehold.co/300x450/1f2937/ffffff?text=${encodeURIComponent(movie.title)}`);
  };

  return (
    <Card 
      className="overflow-hidden transition-all duration-200 hover:scale-105 cursor-pointer bg-card hover:bg-card/80"
      onClick={() => {
        // Record click interaction
        if (movie.movie_id) {
          recordUserInteraction(movie.movie_id, 'click');
        }
        // Call the original onClick handler
        onClick && onClick(movie);
      }}
    >
      <div className="aspect-[2/3] relative overflow-hidden rounded-t-xl">
        <img 
          src={imgSrc} 
          alt={movie.title} 
          className="object-cover w-full h-full"
          loading="lazy"
          onError={handleImageError}
        />
      </div>
      <CardContent className="p-3">
        <h3 className="font-medium text-sm line-clamp-1 text-center">{movie.title}</h3>
      </CardContent>
    </Card>
  );
};

export default MovieCard;