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

export default function AnticipatedPage() {
  const [anticipatedAnimes, setAnticipatedAnimes] = useState<AnticipatedAnime[]>([]);
  const [activeTab, setActiveTab] = useState<string>(''); // Initialize with empty string

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

  // Filter available tabs based on expected order and actual data
  const availableTabs = expectedTabOrderForDisplay.filter(season => groupedAnimes[season] && groupedAnimes[season].length > 0);

  return (
    <main className="container mx-auto px-4 py-8">
      <h1 className="text-4xl font-bold text-center mb-8 text-white">Most Anticipated Anime</h1>
      
      {/* Tabs */}
      <div className="flex justify-center mb-8 space-x-4 flex-wrap">
        {availableTabs.map(season => (
          <button
            key={season}
            onClick={() => setActiveTab(season)}
            className={`px-4 py-2 rounded-lg font-semibold ${
              activeTab === season ? 'bg-blue-600 text-white' : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
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
    </main>
  );
}
