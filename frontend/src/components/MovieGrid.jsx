import React, { useState } from 'react';
import MovieCard from './MovieCard';
import { Button } from './ui/button';

/**
 * MovieGrid component for displaying a grid of movies with pagination
 * @param {Object} props - Component props
 * @param {Array} props.movies - Array of movie objects to display
 * @param {string} props.title - Title for the grid section
 * @param {Function} props.onMovieSelect - Function to call when a movie is selected
 * @returns {JSX.Element} - Rendered component
 */
const MovieGrid = ({ movies, title, onMovieSelect }) => {
  const [currentPage, setCurrentPage] = useState(1);
  const moviesPerPage = 18; // 6 columns x 3 rows on large screens

  if (!movies || movies.length === 0) {
    return null;
  }

  // Calculate pagination
  const indexOfLastMovie = currentPage * moviesPerPage;
  const indexOfFirstMovie = indexOfLastMovie - moviesPerPage;
  const currentMovies = movies.slice(indexOfFirstMovie, indexOfLastMovie);
  const totalPages = Math.ceil(movies.length / moviesPerPage);

  // Change page
  const paginate = (pageNumber) => setCurrentPage(pageNumber);
  const nextPage = () => setCurrentPage((prev) => Math.min(prev + 1, totalPages));
  const prevPage = () => setCurrentPage((prev) => Math.max(prev - 1, 1));

  return (
    <div className="py-6">
      {title && <h2 className="text-2xl font-bold mb-4">{title}</h2>}
      
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-4">
        {currentMovies.map((movie, index) => (
          <div key={movie.id || index} onClick={() => onMovieSelect && onMovieSelect(movie)}>
            <MovieCard movie={movie} />
          </div>
        ))}
      </div>

      {/* Pagination Controls */}
      {totalPages > 1 && (
        <div className="flex justify-center items-center gap-2 mt-8">
          <Button 
            variant="outline" 
            onClick={prevPage} 
            disabled={currentPage === 1}
            size="sm"
          >
            Previous
          </Button>
          
          <div className="flex gap-1">
            {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
              // Show 5 page buttons at most
              let pageNum;
              if (totalPages <= 5) {
                // If 5 or fewer pages, show all
                pageNum = i + 1;
              } else if (currentPage <= 3) {
                // If near the start
                pageNum = i + 1;
              } else if (currentPage >= totalPages - 2) {
                // If near the end
                pageNum = totalPages - 4 + i;
              } else {
                // If in the middle
                pageNum = currentPage - 2 + i;
              }
              
              return (
                <Button
                  key={pageNum}
                  variant={currentPage === pageNum ? "default" : "outline"}
                  size="sm"
                  onClick={() => paginate(pageNum)}
                >
                  {pageNum}
                </Button>
              );
            })}
          </div>
          
          <Button 
            variant="outline" 
            onClick={nextPage} 
            disabled={currentPage === totalPages}
            size="sm"
          >
            Next
          </Button>
        </div>
      )}
    </div>
  );
};

export default MovieGrid;