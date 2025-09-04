import { useState } from 'react'
import Navbar from './components/Navbar'
import HomePage from './components/HomePage'

function App() {
  const [searchQuery, setSearchQuery] = useState('');

  const handleSearch = (query) => {
    setSearchQuery(query);
  };

  return (
    <div className="min-h-screen bg-background text-foreground">
      <Navbar onSearch={handleSearch} />
      <main>
        <HomePage searchQuery={searchQuery} setSearchQuery={setSearchQuery} />
      </main>
      <footer className="border-t py-3 md:py-0">
        <div className="container flex flex-col items-center justify-center gap-4 md:h-16 md:flex-row">
          <p className="text-center text-sm leading-loose text-muted-foreground">
            <strong className='text-[#0f172b]'>© {new Date().getFullYear()} Movie Recommendation Engine.</strong> Developed by Shazid Nawas Shovon. All rights reserved.
          </p>
        </div>
      </footer>
    </div>
  )
}

export default App
