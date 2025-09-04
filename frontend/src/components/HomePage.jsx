import React, { useState, useEffect, useRef } from 'react';
import Hero from './Hero';
import MovieCard from './MovieCard';
import MovieCarousel from './MovieCarousel';
import MovieGrid from './MovieGrid';
import MovieRecommendations from './MovieRecommendations';
import PersonalizedRecommendations from './PersonalizedRecommendations';
import { getAllMovies, searchMovies } from '../services/api';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from './ui/dialog';

/**
 * HomePage component that serves as the main page of the application
 * @param {Object} props - Component props
 * @param {string} props.searchQuery - Search query from the navbar
 * @param {Function} props.setSearchQuery - Setter for search query
 * @returns {JSX.Element} - Rendered component
 */
const HomePage = ({ searchQuery, setSearchQuery }) => {
  const [popularMovies, setPopularMovies] = useState([]);
  const [searchResults, setSearchResults] = useState([]);
  const [selectedMovie, setSelectedMovie] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showHowItWorks, setShowHowItWorks] = useState(false);

  // If user clicks "Browse popular" before section is ready, we queue the scroll
  const [shouldScrollPopular, setShouldScrollPopular] = useState(false);

  const popularMoviesRef = useRef(null);

  // Normalize search query to keep UI visibility consistent with search behavior
  const trimmedQuery = (searchQuery || '').trim();

  // Helper: scroll with offset so the section isn't hidden by a sticky header
  const scrollToWithOffset = (el, offset = 96) => {
    if (!el) return;
    const y = el.getBoundingClientRect().top + window.pageYOffset - offset;
    window.scrollTo({ top: y, behavior: 'smooth' });
  };

  // Fetch all movies on mount
  useEffect(() => {
    const fetchMovies = async () => {
      try {
        setLoading(true);
        const movies = await getAllMovies();
        setPopularMovies(movies);
        setError(null);
      } catch (err) {
        console.error('Error fetching movies:', err);
        setError('Failed to load movies. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    fetchMovies();
  }, []);

  // Handle search query changes (using trimmedQuery)
  useEffect(() => {
    const handleSearch = async () => {
      if (!trimmedQuery) {
        setSearchResults([]);
        return;
      }

      try {
        setLoading(true);
        // Clear stale results so we show the loader instead of old content
        setSearchResults([]);
        const results = await searchMovies(trimmedQuery);
        setSearchResults(results);
        setError(null);
      } catch (err) {
        console.error('Error searching movies:', err);
        setError('Failed to search movies. Please try again.');
      } finally {
        setLoading(false);
      }
    };

    handleSearch();
  }, [trimmedQuery]);

  // If we queued a scroll to popular, run it when the section exists and is visible
  useEffect(() => {
    if (shouldScrollPopular && popularMoviesRef.current && !loading && !trimmedQuery) {
      scrollToWithOffset(popularMoviesRef.current);
      setShouldScrollPopular(false);
    }
  }, [shouldScrollPopular, loading, trimmedQuery]);

  // Handle movie selection for recommendations
  const handleMovieSelect = (movie) => {
    setSelectedMovie(movie);
    // Scroll to recommendations section
    setTimeout(() => {
      document.getElementById('recommendations')?.scrollIntoView({
        behavior: 'smooth',
        block: 'start'
      });
    }, 100);
  };

  // Browse Popular button handler
  const handleBrowsePopularClick = () => {
    // If currently in search mode, clear the query so the section becomes visible, then queue the scroll
    if (trimmedQuery) {
      setSearchQuery('');
      setShouldScrollPopular(true);
      return;
    }
    if (popularMoviesRef.current) {
      scrollToWithOffset(popularMoviesRef.current);
    } else {
      setShouldScrollPopular(true);
    }
  };

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <Hero
        onBrowsePopularClick={handleBrowsePopularClick}
        onHowItWorksClick={() => setShowHowItWorks(true)}
      />

      <div className="container mx-auto px-4 py-8">
        {/* Error State */}
        {error && (
          <div className="bg-destructive/10 text-destructive p-4 rounded-md my-6">
            {error}
          </div>
        )}

        {/* Loader
            - Initial load (no search): "Loading movies..."
            - During search: "Searching..."
        */}
        {loading && (
          <div className="flex flex-col items-center justify-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary" />
            <p className="mt-4 text-sm text-muted-foreground">
              {trimmedQuery ? 'Searching…' : 'Loading movies…'}
            </p>
          </div>
        )}

        {/* Search Results */}
        {trimmedQuery && !loading && searchResults.length > 0 && (
          <div className="mb-12">
            <MovieGrid
              movies={searchResults}
              title={`Search Results for "${trimmedQuery}"`}
              onMovieSelect={handleMovieSelect}
            />
          </div>
        )}

        {/* No Search Results */}
        {trimmedQuery && !loading && searchResults.length === 0 && !error && (
          <div className="text-center py-12">
            <h2 className="text-2xl font-bold mb-2">No results found for "{trimmedQuery}"</h2>
            <p className="text-muted-foreground">Try a different search term or browse our popular movies below.</p>
          </div>
        )}

        {/* Popular Movies Carousel (initially visible; hidden during search or while loading) */}
        {!trimmedQuery && !loading && popularMovies && (
          <div
            ref={popularMoviesRef}
            id="popular"
            className="scroll-mt-24" // adjust if your navbar is taller/shorter
          >
            <MovieCarousel
              movies={popularMovies.movies || popularMovies}
              title="Popular Movies"
              onMovieSelect={handleMovieSelect}
              dynamicLoading={true}
            />
          </div>
        )}

        {/* Personalized Recommendations (hidden during search or while loading) */}
        {!trimmedQuery && !loading && (
          <PersonalizedRecommendations onMovieSelect={handleMovieSelect} />
        )}

        {/* How It Works Dialog */}
        <Dialog open={showHowItWorks} onOpenChange={setShowHowItWorks}>
          <DialogContent className="max-w-2xl">
            <DialogHeader>
              <DialogTitle className="text-2xl font-bold">How Our Movie Recommender Works</DialogTitle>
            </DialogHeader>
            <DialogDescription className="space-y-4 py-4">
              <p>
                Our movie recommendation system uses a hybrid approach combining content-based and collaborative filtering:
              </p>
              <div className="space-y-2">
                <h3 className="font-semibold text-lg">Content-Based Recommendations</h3>
                <p>
                  We analyze movie attributes like genres, actors, directors, and plot keywords to find similar movies
                  that match your interests based on what you&apos;ve watched or liked before.
                </p>
              </div>
              <div className="space-y-2">
                <h3 className="font-semibold text-lg">Collaborative Filtering</h3>
                <p>
                  We identify patterns among users with similar tastes to yours. If someone with similar preferences
                  enjoyed a movie you haven&apos;t seen yet, we&apos;ll recommend it to you.
                </p>
              </div>
              <div className="space-y-2">
                <h3 className="font-semibold text-lg">Personalized Experience</h3>
                <p>
                  The more you interact with movies (viewing details, clicking, rating), the better our recommendations
                  become. Your recommendations are continuously updated as you use the system.
                </p>
              </div>
            </DialogDescription>
          </DialogContent>
        </Dialog>

        {/* Recommendations Section */}
        <div id="recommendations">
          <MovieRecommendations
            selectedMovie={selectedMovie}
            onMovieSelect={handleMovieSelect}
          />
        </div>
      </div>
    </div>
  );
};

export default HomePage;
