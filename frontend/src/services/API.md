# API Service Documentation

## Overview

The API service (`api.js`) provides an interface for the frontend to communicate with the backend. Currently, it uses mock data for development purposes, but it can be easily adapted to connect to the actual Flask API backend.

## Available Methods

### `getAllMovies()`

Fetches a list of all available movies.

```javascript
import { getAllMovies } from './services/api';

// Usage
getAllMovies().then(movies => {
  console.log(movies);
});
```

### `searchMovies(query)`

Searches for movies based on a query string.

```javascript
import { searchMovies } from './services/api';

// Usage
searchMovies('inception').then(results => {
  console.log(results);
});
```

### `getMovieRecommendations(movieId)`

Fetches movie recommendations based on a selected movie ID.

```javascript
import { getMovieRecommendations } from './services/api';

// Usage
getMovieRecommendations('123').then(recommendations => {
  console.log(recommendations);
});
```

## Integration with Flask API Backend

To connect this API service with the actual Flask API backend:

1. Update the API endpoints in the service methods to point to your Flask API server
2. Ensure proper error handling for API requests
3. Configure CORS on the Flask API backend to accept requests from the frontend

### Example Integration

```javascript
// Example of updating the getAllMovies function to connect to a real backend
export const getAllMovies = async () => {
  try {
    const response = await fetch('http://localhost:5000/search?query=');
    const data = await response.json();
    return data.movies;
  } catch (error) {
    console.error('Error fetching movies:', error);
    return [];
  }
};
```

## Data Structure

The API service expects and returns data in the following format:

### Movie Object

```javascript
{
  id: string,
  title: string,
  poster_path: string,
  overview: string,
  release_date: string,
  vote_average: number
}
```

## Error Handling

All API methods include basic error handling and will reject the promise with an appropriate error message if the request fails.