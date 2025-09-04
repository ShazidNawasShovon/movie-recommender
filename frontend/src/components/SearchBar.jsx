import React, { useState } from 'react';
import { Input } from './ui/input';
import { Button } from './ui/button';

/**
 * SearchBar component for searching movies
 * @param {Object} props - Component props
 * @param {Function} props.onSearch - Function to call when search is submitted
 * @returns {JSX.Element} - Rendered component
 */
const SearchBar = ({ onSearch }) => {
  const [query, setQuery] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (query.trim()) {
      onSearch(query.trim());
    }
  };

  return (
    <form onSubmit={handleSubmit} className="flex w-full max-w-lg gap-2">
      <Input
        type="text"
        placeholder="Search for movies..."
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        className="flex-1"
      />
      <Button type="submit" className="bg-primary hover:bg-primary/90">
        Search
      </Button>
    </form>
  );
};

export default SearchBar;