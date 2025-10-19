'use client'; // This component uses client-side features like useState

import React, { useState, useEffect } from 'react';
import AnticipatedAnimeCard from '../../components/AnticipatedAnimeCard';

type AnticipatedAnime = {
  id: number;
  title: string;
  image_url: string;
  members: number;
  season: string;
  year: number;
  mal_url: string;
};

async function getAnticipatedAnimesClient(): Promise<AnticipatedAnime[]> {
  const response = await fetch('/anticipated_animes_data.json');
  if (!response.ok) {
    console.error('Failed to fetch anticipated animes:', response.statusText);
    return [];
  }
  return response.json();
}

// Helper to get current season and year
function getCurrentSeasonAndYear(): { season: string; year: number } {
  const now = new Date();
  const month = now.getMonth();
  const year = now.getFullYear();

  let season = '';
  if (month >= 2 && month <= 4) { // March, April, May
    season = 'Spring';
  } else if (month >= 5 && month <= 7) { // June, July, August
    season = 'Summer';
  } else if (month >= 8 && month <= 10) { // September, October, November
    season = 'Fall';
  } else { // December, January, February
    season = 'Winter';
  }
  return { season, year };
}

// Helper to get next N seasons
function getNextSeasons(currentSeason: string, currentYear: number, count: number): { season: string; year: number }[] {
  const seasons = ['Winter', 'Spring', 'Summer', 'Fall'];
  let currentSeasonIndex = seasons.indexOf(currentSeason);
  let currentYearAdjusted = currentYear;
  const nextSeasons: { season: string; year: number }[] = [];

  for (let i = 0; i < count; i++) {
    currentSeasonIndex++;
    if (currentSeasonIndex >= seasons.length) {
      currentSeasonIndex = 0;
      currentYearAdjusted++;
    }
    nextSeasons.push({ season: seasons[currentSeasonIndex], year: currentYearAdjusted });
  }
  return nextSeasons;
}

// Helper to sort seasons chronologically
function sortSeasonsChronologically(seasonKeys: string[]): string[] {
  const seasonOrderMap: { [key: string]: number } = {
    'Winter': 0, 'Spring': 1, 'Summer': 2, 'Fall': 3
  };

  return seasonKeys.sort((a, b) => {
    if (a === 'Later') return 1;
    if (b === 'Later') return -1;

    const [seasonA, yearA] = a.split(' ');
    const [seasonB, yearB] = b.split(' ');

    if (parseInt(yearA) !== parseInt(yearB)) {
      return parseInt(yearA) - parseInt(yearB);
    }
    return seasonOrderMap[seasonA] - seasonOrderMap[seasonB];
  });
}

export default function AnticipatedPage() {
  const [anticipatedAnimes, setAnticipatedAnimes] = useState<AnticipatedAnime[]>([]);
  const [activeTab, setActiveTab] = useState<string>(''); // Initialize with empty string
  const [isTransitioning, setIsTransitioning] = useState(false);

  // Smooth transition function for season changes
  const handleSeasonChange = (newSeason: string) => {
    if (newSeason === activeTab) return;
    
    setIsTransitioning(true);
    setTimeout(() => {
      setActiveTab(newSeason);
      setTimeout(() => {
        setIsTransitioning(false);
      }, 150);
    }, 150); // Half of the transition duration
  };

  useEffect(() => {
    getAnticipatedAnimesClient().then(data => {
      setAnticipatedAnimes(data);
      
      const { season: currentSeason, year: currentYear } = getCurrentSeasonAndYear();
      const nextTwoSeasons = getNextSeasons(currentSeason, currentYear, 2);

      const expectedTabOrderForDisplay = [
        `${currentSeason} ${currentYear}`,
        ...nextTwoSeasons.map(s => `${s.season} ${s.year}`),
        'Later' // Always include Later for display
      ];

      // Group animes by season and year
      const groupedAnimes = data.reduce((acc, anime) => {
        let seasonKey = 'Later'; // Default to Later

        if (anime.season && anime.year) {
          const animeSeasonYear = `${anime.season.charAt(0).toUpperCase() + anime.season.slice(1)} ${anime.year}`;
          if (expectedTabOrderForDisplay.includes(animeSeasonYear)) { // Only group into specific tabs if it's one of the expected display tabs
            seasonKey = animeSeasonYear;
          }
        }
        
        if (!acc[seasonKey]) {
          acc[seasonKey] = [];
        }
        acc[seasonKey].push(anime);
        return acc;
      }, {} as Record<string, AnticipatedAnime[]>);

      // Dynamically generate tab order based on available seasons and sort chronologically
      const initialAvailableTabs = sortSeasonsChronologically(Object.keys(groupedAnimes));

      if (initialAvailableTabs.length > 0) {
        setActiveTab(initialAvailableTabs[0]);
      } else {
        // Fallback if no expected seasons have data, just show 'Later' if available
        if (groupedAnimes['Later'] && groupedAnimes['Later'].length > 0) {
          setActiveTab('Later');
        }
      }
    });
  }, []);

  // Group animes by season and year (re-calculated for rendering)
  const { season: currentSeason, year: currentYear } = getCurrentSeasonAndYear();
  const nextTwoSeasons = getNextSeasons(currentSeason, currentYear, 2);

  const expectedTabOrderForDisplay = [
    `${currentSeason} ${currentYear}`,
    ...nextTwoSeasons.map(s => `${s.season} ${s.year}`),
    'Later' // Always include Later for display
  ];

  const groupedAnimes = anticipatedAnimes.reduce((acc, anime) => {
    let seasonKey = 'Later'; // Default to Later

    if (anime.season && anime.year) {
      const animeSeasonYear = `${anime.season.charAt(0).toUpperCase() + anime.season.slice(1)} ${anime.year}`;
      if (expectedTabOrderForDisplay.includes(animeSeasonYear)) { // Only group into specific tabs if it's one of the expected display tabs
        seasonKey = animeSeasonYear;
      }
    }
    
    if (!acc[seasonKey]) {
      acc[seasonKey] = [];
    }
    acc[seasonKey].push(anime);
    return acc;
  }, {} as Record<string, AnticipatedAnime[]>);

  // Sort each group by members count (descending)
  Object.keys(groupedAnimes).forEach(season => {
    groupedAnimes[season].sort((a, b) => b.members - a.members);
  });

  // Filter available tabs based on expected order and actual data
  const availableTabs = expectedTabOrderForDisplay.filter(season => groupedAnimes[season] && groupedAnimes[season].length > 0);

  const firstPlaceImage = groupedAnimes[activeTab] && groupedAnimes[activeTab].length > 0 ? groupedAnimes[activeTab][0].image_url : null;

  return (
    <main 
      className={`container mx-auto px-4 pt-8 pb-8 min-h-screen ${firstPlaceImage ? 'dynamic-background' : ''}`}
      style={{
        background: firstPlaceImage ? 'transparent' : 'var(--background)',
        ...(firstPlaceImage && { '--bg-image': `url("${firstPlaceImage}")` } as React.CSSProperties)
      }}
    >
      <div className="dynamic-background-content">
        <h1 className="text-4xl font-bold text-center mb-2" style={{color: 'var(--foreground)'}}>
          Most Anticipated Anime
        </h1>
        <p className="text-center mb-8 text-sm period-subtitle period-transition">
          Discover the most anticipated anime by season
        </p>
        
        {/* Tabs */}
        <div className="flex justify-center mb-8">
          <div className="flex space-x-2 theme-card rounded-lg p-1">
            {availableTabs.map(season => (
              <button
                key={season}
                onClick={() => handleSeasonChange(season)}
                className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                  activeTab === season ? 'theme-rank' : 'theme-nav-link'
                }`}
              >
                {season}
              </button>
            ))}
          </div>
        </div>

        {/* Anime Cards for active tab */}
        <div className={`grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6 content-grid ${isTransitioning ? 'loading' : ''}`}>
          {groupedAnimes[activeTab]?.map((anime, index) => (
            <AnticipatedAnimeCard key={anime.id} anime={anime} rank={index + 1} />
          ))}
        </div>
      </div>
    </main>
  );
}
