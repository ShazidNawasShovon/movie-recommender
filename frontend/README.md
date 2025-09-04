# Movie Recommender Frontend

A modern React frontend for the Movie Recommender system, built with Vite, React, Tailwind CSS, and ShadcnUI components.

## Features

- **Modern UI**: Clean and responsive design inspired by streaming platforms
- **Movie Recommendations**: Get personalized movie recommendations based on selected movies
- **Search Functionality**: Search for movies by title
- **Movie Carousels**: Browse popular movies in an interactive carousel
- **Hybrid Recommendation System**: Combines content-based and collaborative filtering for better recommendations
- **Responsive Design**: Works on desktop and mobile devices

## How to Use

1. **Search for Movies**: Use the search bar at the top to find movies by title
2. **View Movie Details**: Click on a movie card to see more information
3. **Get Recommendations**: Click the "Get Recommendations" button on a movie card to see similar movies
4. **Browse Popular Movies**: Scroll through the carousel to discover popular movies

## Tech Stack

- **React**: Frontend library for building user interfaces
- **Vite**: Next-generation frontend tooling
- **Tailwind CSS**: Utility-first CSS framework
- **ShadcnUI**: Beautifully designed components built with Radix UI and Tailwind CSS
- **Embla Carousel**: Lightweight carousel component for the web

## Project Structure

```
frontend/
├── public/            # Static assets
├── src/
│   ├── components/    # React components
│   │   ├── ui/        # ShadcnUI components
│   │   └── ...        # Custom components
│   ├── lib/           # Utility functions
│   ├── services/      # API services
│   ├── App.jsx        # Main application component
│   ├── main.jsx       # Application entry point
│   └── index.css      # Global styles
├── index.html         # HTML template
└── package.json       # Project dependencies
```

## Setup and Installation

### Deployment to Netlify

The frontend is configured for easy deployment on Netlify's free tier:

1. Fork or clone this repository to your GitHub account
2. Sign up for a free account at [netlify.com](https://netlify.com/)
3. From the Netlify dashboard, click "New site from Git"
4. Connect your GitHub repository
5. Configure the build settings:
   - **Base directory**: `frontend` (since the React app is in a subdirectory)
   - **Build command**: `npm run build`
   - **Publish directory**: `dist` (for Vite projects)

6. Add the following environment variable:
   - `REACT_APP_API_URL`: Your Render backend URL (e.g., https://movie-recommender-api.onrender.com)

7. Click "Deploy site"

Netlify will deploy your frontend and provide you with a URL like `https://movie-recommender.netlify.app`

### Connecting to Backend

Before deploying, update the API URL in `src/services/api.js`:

```javascript
// Replace this line
const API_URL = 'http://localhost:8502';

// With this
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8502';
```

Then create a `.env.production` file in the frontend directory:

```
VITE_API_URL=https://your-render-backend-url.onrender.com
```

### Local Development Prerequisites

- Node.js (v14 or later)
- npm or yarn

### Installation

1. Clone the repository
   ```bash
   git clone https://github.com/ShazidNawasShovon/movie-recommender.git
   cd movie-recommender/frontend
   ```

2. Install dependencies
   ```bash
   npm install
   ```

3. Start the development server
   ```bash
   npm run dev
   ```

4. Open your browser and navigate to `http://localhost:5173`

## Integration with Backend

The frontend connects to the Flask API backend through the API service located in `src/services/api.js`. To connect to the Flask backend:

1. Ensure the Flask backend is running on port 8502 (default configuration)
2. The API endpoints in `src/services/api.js` are configured to connect to `http://localhost:8502`
3. CORS is already configured on the backend to allow requests from the frontend

### API Endpoints

The frontend uses the following API endpoints:

- `GET /search?query=<search_term>` - Search for movies by title
- `GET /recommend?movie_id=<movie_id>` - Get movie recommendations based on a selected movie
- `GET /movies` - Get a list of all movies (used for initial loading)

### Running Both Frontend and Backend

For the complete application experience:

1. Start the Flask backend first:
   ```bash
   # From the project root directory
   python api_server.py
   ```

2. Start the React frontend in a separate terminal:
   ```bash
   # From the frontend directory
   npm run dev
   ```

3. Access the application at `http://localhost:5173`

## Available Scripts

- `npm run dev` - Start the development server
- `npm run build` - Build the application for production
- `npm run preview` - Preview the production build locally

## TMDB Attribution

This product uses the TMDB API but is not endorsed or certified by TMDB. All movie data and images are provided by The Movie Database (TMDB) API.

## Future Enhancements

- **Movie Details Page**: Expanded view with cast, crew, and additional metadata
- **User Authentication**: Login and registration functionality
- **User Profiles**: Personalized recommendations based on user history
- **Favorites and Watchlist**: Save movies to watch later or mark as favorites
- **Advanced Filtering**: Filter by genre, year, rating, and other criteria
- **Social Features**: Share recommendations with friends
- **Dark/Light Mode**: Toggle between dark and light themes
- **Offline Support**: Basic functionality when offline using cached data

## Contributing

Contributions are welcome! Here's how you can contribute to the project:

1. Fork the repository
2. Create a new branch (`git checkout -b feature/your-feature-name`)
3. Make your changes
4. Commit your changes (`git commit -m 'Add some feature'`)
5. Push to the branch (`git push origin feature/your-feature-name`)
6. Open a Pull Request

Please make sure to update tests as appropriate and follow the code style of the project.
