import React from 'react';
import { Button } from './ui/button';

/**
 * Hero component for the homepage banner
 * @param {Object} props - Component props
 * @param {Function} props.onBrowsePopularClick - Function to call when Browse Popular Movies is clicked
 * @param {Function} props.onHowItWorksClick - Function to call when How It Works is clicked
 * @returns {JSX.Element} - Rendered component
 */
const Hero = ({ onBrowsePopularClick, onHowItWorksClick }) => {
  return (
    <div className="relative overflow-hidden bg-gradient-to-b from-primary/20 to-background py-12 md:py-24">
      <div className="container mx-auto px-4 relative z-10">
        <div className="max-w-3xl">
          <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold tracking-tight mb-4">
            Discover Your Next <span className="text-primary">Favorite Movie</span>
          </h1>
          <p className="text-xl md:text-2xl text-muted-foreground mb-8">
            Get personalized movie recommendations based on your taste. Find hidden gems and blockbusters you'll love.
          </p>
          <div className="flex flex-col sm:flex-row gap-4">
            <Button 
              size="lg" 
              className="font-medium cursor-pointer"
              onClick={onBrowsePopularClick}
            >
              Browse Popular Movies
            </Button>
            <Button 
              size="lg" 
              variant="outline" 
              className="font-medium cursor-pointer"
              onClick={onHowItWorksClick}
            >
              How It Works
            </Button>
          </div>
        </div>
      </div>
      
      {/* Abstract background elements */}
      <div className="absolute top-1/2 right-0 transform -translate-y-1/2 w-1/2 h-full opacity-20">
        <div className="absolute top-1/4 right-1/4 w-64 h-64 rounded-full bg-primary blur-3xl"></div>
        <div className="absolute bottom-1/4 right-1/3 w-96 h-96 rounded-full bg-secondary blur-3xl"></div>
      </div>
    </div>
  );
};

export default Hero;