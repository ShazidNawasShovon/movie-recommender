import React, { useState, useEffect, useCallback } from 'react';
import { Swiper, SwiperSlide } from 'swiper/react';
import { Navigation, Pagination } from 'swiper/modules';
import MovieCard from './MovieCard';
import { getAllMovies } from '../services/api';

// Import Swiper styles
import 'swiper/css';
import 'swiper/css/navigation';
import 'swiper/css/pagination';

/**
 * MovieCarousel component for displaying a horizontal scrollable list of movies
 * @param {Object} props - Component props
 * @param {Array} props.movies - Array of movie objects to display
 * @param {string} props.title - Title for the carousel section
 * @param {Function} props.onMovieSelect - Function to call when a movie is selected
 * @param {boolean} props.dynamicLoading - Whether to enable dynamic loading of more movies
 * @returns {JSX.Element} - Rendered component
 */
const MovieCarousel = ({ movies: initialMovies, title, onMovieSelect, dynamicLoading = false }) => {
  const [movies, setMovies] = useState(initialMovies || []);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(false);
  const [hasMore, setHasMore] = useState(true);

  if (!movies || movies.length === 0) {
    return null;
  }

  // Function to load more movies when needed
  const loadMoreMovies = useCallback(async () => {
    if (!dynamicLoading || loading || !hasMore) return;
    
    try {
      setLoading(true);
      const nextPage = page + 1;
      const response = await getAllMovies(nextPage, 15);
      
      if (response.movies && response.movies.length > 0) {
        setMovies(prevMovies => [...prevMovies, ...response.movies]);
        setPage(nextPage);
        setHasMore(response.pagination.has_next);
      } else {
        setHasMore(false);
      }
    } catch (error) {
      console.error('Error loading more movies:', error);
    } finally {
      setLoading(false);
    }
  }, [dynamicLoading, page, loading, hasMore]);

  // Update movies when initialMovies changes
  useEffect(() => {
    if (initialMovies && initialMovies.length > 0) {
      setMovies(initialMovies);
    }
  }, [initialMovies]);

  return (
    <div className="py-6">
      {title && (
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-2xl font-bold">{title}</h2>
          {dynamicLoading && (
            <div className="flex gap-2">
              <span className="text-sm text-muted-foreground">
                Page {page}
              </span>
            </div>
          )}
        </div>
      )}
      <div className="relative">
        <Swiper
          modules={[Navigation, Pagination]}
          spaceBetween={16}
          slidesPerView={1.2}
          breakpoints={{
            640: { slidesPerView: 2.2 },
            768: { slidesPerView: 3.2 },
            1024: { slidesPerView: 4.2 },
            1280: { slidesPerView: 5.2 },
          }}
          navigation
          pagination={{ clickable: true, dynamicBullets: true }}
          className="movie-swiper"
          onReachEnd={() => {
            if (dynamicLoading) {
              loadMoreMovies();
            }
          }}
        >
          {movies.map((movie, index) => (
            <SwiperSlide key={movie.id || index}>
              <MovieCard movie={movie} onClick={onMovieSelect} />
            </SwiperSlide>
          ))}
          {loading && (
            <SwiperSlide>
              <div className="flex items-center justify-center h-full min-h-[300px]">
                <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary"></div>
              </div>
            </SwiperSlide>
          )}
        </Swiper>
      </div>
    </div>
  );
};

export default MovieCarousel;