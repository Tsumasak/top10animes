'use client'; // This component uses client-side features like useState

import React, { useState, useEffect } from 'react';
import AnticipatedAnimeCard from '@/components/AnticipatedAnimeCard';

type AnticipatedAnime = {
  id: number;
  title: string;
  image_url: string;
  members: number;
  season: string;
  year: number;
  mal_url: string;
};

interface UpdateMetadata {
  last_updated: string;
  episodes_period: {
    start_date: string;
    end_date: string;
  };
  anticipated_update_date: string;
}

async function getAnticipatedAnimesClient(): Promise<AnticipatedAnime[]> {
  const response = await fetch('/anticipated_animes_data.json');
  if (!response.ok) {
    console.error('Failed to fetch anticipated animes:', response.statusText);
    return [];
  }
  return response.json();
}

async function getUpdateMetadataClient(): Promise<UpdateMetadata> {
  try {
    const response = await fetch('/update_metadata.json');
    if (!response.ok) throw new Error('No metadata file');
    return response.json();
  } catch (error) {
    // Fallback to default values if metadata file doesn't exist
    return {
      last_updated: new Date().toISOString(),
      episodes_period: {
        start_date: "2025-10-06",
        end_date: "2025-10-12"
      },
      anticipated_update_date: "2025-10-16"
    };
  }
}

// Helper to get current season and year
function getCurrentSeasonAndYear(): { season: string; year: number } {
  const now = new Date();
  const month = now.getMonth(); // 0-based: 0=Jan, 1=Feb, ..., 11=Dec
  const year = now.getFullYear();

  let season = '';
  if (month >= 2 && month <= 4) { // March (2), April (3), May (4)
    season = 'Spring';
  } else if (month >= 5 && month <= 7) { // June (5), July (6), August (7)
    season = 'Summer';
  } else if (month >= 8 && month <= 10) { // September (8), October (9), November (10)
    season = 'Fall';
  } else { // December (11), January (0), February (1)
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

// Helper function to format update date from metadata
function getAnticipatedPeriod(metadata: UpdateMetadata): string {
  // Parse date string manually to avoid timezone issues
  const [year, month, day] = metadata.anticipated_update_date.split('-').map(Number);
  const date = new Date(year, month - 1, day); // month is 0-indexed in JS
  const formattedDate = date.toLocaleDateString('en-US', { 
    month: 'short', 
    day: 'numeric', 
    year: 'numeric' 
  });
  
  return `Updated - ${formattedDate}`;
}

export default function AnticipatedPage() {
  const [anticipatedAnimes, setAnticipatedAnimes] = useState<AnticipatedAnime[]>([]);
  const [metadata, setMetadata] = useState<UpdateMetadata | null>(null);
  const [activeTab, setActiveTab] = useState<string>(''); // Initialize with empty string

  useEffect(() => {
    // Load both animes and metadata
    Promise.all([getAnticipatedAnimesClient(), getUpdateMetadataClient()]).then(([data, meta]) => {
      setAnticipatedAnimes(data);
      setMetadata(meta);
      
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

  // Filter available tabs based on expected order and actual data
  const availableTabs = expectedTabOrderForDisplay.filter(season => groupedAnimes[season] && groupedAnimes[season].length > 0);
  
  // Get the first place anime image for background from active tab
  const activeTabAnimes = groupedAnimes[activeTab] || [];
  const firstPlaceImage = activeTabAnimes.length > 0 ? activeTabAnimes[0].image_url : null;

  return (
    <main 
      className={`container mx-auto px-4 pt-8 pb-8 min-h-screen ${firstPlaceImage ? 'dynamic-background' : ''}`}
      style={{
        background: firstPlaceImage ? 'transparent' : 'var(--background)',
        ...(firstPlaceImage && { '--bg-image': `url("${firstPlaceImage}")` } as React.CSSProperties)
      }}
    >
      <div className="dynamic-background-content">
        <h1 className="text-4xl font-bold text-center mb-2" style={{color: 'var(--foreground)'}}>Most Anticipated Anime</h1>
        <p className="text-center mb-8 text-sm period-subtitle">
          {metadata ? getAnticipatedPeriod(metadata) : 'Loading...'}
        </p>
        
        {/* Tabs */}
        <div className="flex justify-center mb-8 space-x-4 flex-wrap">
          {availableTabs.map(season => (
            <button
              key={season}
              onClick={() => setActiveTab(season)}
              className={`px-4 py-2 rounded-lg font-semibold transition-colors ${
                activeTab === season 
                  ? 'theme-rank' 
                  : 'theme-card hover:theme-card-hover'
              }`}
            >
              {season}
            </button>
          ))}
        </div>

        {/* Anime Cards for active tab */}
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
          {groupedAnimes[activeTab]?.slice(0, 25).map((anime, index) => (
            <AnticipatedAnimeCard key={anime.id} anime={anime} rank={index + 1} />
          ))}
        </div>
      </div>
    </main>
  );
}
