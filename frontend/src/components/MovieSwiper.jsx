import React, { useState, useEffect, useRef } from 'react';
import MovieCard from './MovieCard';
import { getAllMovies } from '../services/api';

/**
 * MovieSwiper component for displaying movies with Swiper.js and pagination
 * @param {Object} props - Component props
 * @param {Function} props.onMovieSelect - Function to call when a movie is selected
 * @returns {JSX.Element} - Rendered component
 */
const MovieSwiper = ({ onMovieSelect }) => {
  const [movies, setMovies] = useState([]);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [loading, setLoading] = useState(false);
  const [hasMore, setHasMore] = useState(true);
  const containerRef = useRef(null);
  const [isMounted, setIsMounted] = useState(false);

  const loadMovies = async (page = 1) => {
    try {
      setLoading(true);
      const response = await getAllMovies(page, 15);
      const { movies: newMovies, pagination } = response;
      
      if (page === 1) {
        setMovies(newMovies);
      } else {
        setMovies(prev => [...prev, ...newMovies]);
      }
      
      setCurrentPage(pagination.page);
      setTotalPages(pagination.total_pages);
      setHasMore(pagination.has_next);
    } catch (error) {
      console.error('Error loading movies:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    setIsMounted(true);
    loadMovies(1);
    
    return () => setIsMounted(false);
  }, []);

  const handleReachEnd = () => {
    if (hasMore && !loading) {
      loadMovies(currentPage + 1);
    }
  };

  // Scroll to end when new movies are loaded
  useEffect(() => {
    if (isMounted && movies.length > 0 && containerRef.current) {
      // Auto-scroll to show new content
      containerRef.current.scrollLeft = containerRef.current.scrollWidth;
    }
  }, [movies, isMounted]);

  return (
    <div className="py-6">
      <h2 className="text-2xl font-bold mb-4">All Movies</h2>
      
      <div 
        ref={containerRef}
        className="flex overflow-x-auto space-x-4 pb-4 scrollbar-hide"
        style={{ scrollbarWidth: 'none', msOverflowStyle: 'none' }}
      >
        {movies.map((movie, index) => (
          <div key={index} className="flex-shrink-0 w-48">
            <MovieCard movie={movie} onClick={onMovieSelect} />
          </div>
        ))}
      </div>

      {loading && (
        <div className="flex justify-center mt-4">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
        </div>
      )}

      <div className="flex justify-center mt-4 text-sm text-muted-foreground">
        Page {currentPage} of {totalPages} • {movies.length} movies loaded
      </div>
    </div>
  );
};

export default MovieSwiper;