import React from 'react';
import SearchBar from './SearchBar';
import { TvMinimalPlay } from 'lucide-react';
import { Link } from '@radix-ui/react-navigation-menu';

/**
 * Navbar component for the application header
 * @param {Object} props - Component props
 * @param {Function} props.onSearch - Function to call when search is submitted
 * @returns {JSX.Element} - Rendered component
 */
const Navbar = ({ onSearch }) => {
  return (
    <header className="sticky top-0 z-40 w-full border-b bg-gradient-to-b from-primary/20 to-background backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-16 items-center justify-between py-4">
        <a href="/" className="flex items-center gap-1">
          <img src="/logo_movie_r.png" alt="Movie Recommendation Logo" className="h-10 w-10" />
          <h1 className="text-xl font-bold italic">Movie Recommendation Engine</h1>
        </a>
        
        <div className="hidden md:block">
          <SearchBar onSearch={onSearch} />
        </div>
        
        <div className="flex items-center gap-4">
          {/* Mobile search button */}
          <button className="md:hidden rounded-full p-2 hover:bg-accent">
            <svg 
              xmlns="http://www.w3.org/2000/svg" 
              viewBox="0 0 24 24" 
              fill="none" 
              stroke="currentColor" 
              strokeWidth="2" 
              strokeLinecap="round" 
              strokeLinejoin="round" 
              className="h-5 w-5"
            >
              <circle cx="11" cy="11" r="8" />
              <path d="m21 21-4.3-4.3" />
            </svg>
          </button>
        </div>
      </div>
      
      {/* Mobile search bar */}
      <div className="md:hidden px-4 pb-4">
        <SearchBar onSearch={onSearch} />
      </div>
    </header>
  );
};

export default Navbar;