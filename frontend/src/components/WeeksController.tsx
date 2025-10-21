'use client';

import { useState, useEffect, useRef } from 'react';
import EpisodeCard from './EpisodeCard';
import BlankState from './BlankState';
import { WEEKS_DATA, CURRENT_WEEK_NUMBER, getCurrentWeek, WeekData } from '../config/weeks';

interface Episode {
  anime_id: number;
  anime_title: string;
  title: string;
  episode_number: number;
  rating: number;
  anime_image_url: string;
  episode_url: string;
  anime_type: string;
}

// Function to get the formatted period with correct "Aired" or "Airing" prefix
const getFormattedPeriod = (week: WeekData, isCurrentWeek: boolean): string => {
  const prefix = isCurrentWeek ? 'Airing' : 'Aired';
  // Extract the date range from the period, removing the original prefix
  const dateRange = week.period.replace(/^(Aired|Airing) - /, '');
  return `${prefix} - ${dateRange}`;
};

// Function to calculate position change for an ANIME (not specific episode)
const calculatePositionChange = (
  episode: Episode,
  currentRank: number,
  previousWeekEpisodes: Episode[]
): number | undefined => {
  if (previousWeekEpisodes.length === 0) {
    return undefined; // No previous data, mark as new
  }

  // Find any episode of the same ANIME in previous week data (regardless of episode number)
  const previousAnimeEpisode = previousWeekEpisodes.find(
    prevEp => prevEp.anime_id === episode.anime_id
  );

  if (!previousAnimeEpisode) {
    return undefined; // Anime not found in previous week, mark as new
  }

  // Find the rank of that anime in previous week
  const previousRank = previousWeekEpisodes.findIndex(
    prevEp => prevEp.anime_id === episode.anime_id
  ) + 1;

  // Calculate position change (positive = went up, negative = went down)
  return previousRank - currentRank;
};

// Trend indicators system - dynamic week detection
const getTrendIndicator = (rank: number, weekId: string) => {
  const currentWeekId = `week${CURRENT_WEEK_NUMBER}`;
  const weekNum = parseInt(weekId.replace('week', ''));
  
  if (weekId === currentWeekId) {
    // Current week - Hot trends
    if (rank <= 3) return { symbol: '🔥', color: '#ef4444' }; // Red for hot
    if (rank <= 6) return { symbol: '⬆️', color: '#22c55e' }; // Green for rising
    if (rank <= 10) return { symbol: '=', color: '#6b7280' }; // Gray for stable
    return { symbol: '⬇️', color: '#f97316' }; // Orange for falling
  }
  
  if (weekNum === CURRENT_WEEK_NUMBER - 1) {
    // Previous week - Trending indicators
    if (rank <= 5) return { symbol: '🆕', color: '#3b82f6' }; // Blue for new
    if (rank <= 10) return { symbol: '⬆️', color: '#22c55e' }; // Green for rising
    return { symbol: '=', color: '#6b7280' }; // Gray for stable
  }
  
  if (weekNum <= CURRENT_WEEK_NUMBER - 2) {
    // Older weeks - Historical data
    if (rank <= 5) return { symbol: '⬆️', color: '#22c55e' }; // Green for good performance
    return { symbol: '=', color: '#6b7280' }; // Gray for average
  }
  
  // Future weeks
  if (weekNum > CURRENT_WEEK_NUMBER) {
    return { symbol: '⏳', color: '#9333ea' }; // Purple for upcoming
  }
  
  return { symbol: '=', color: '#6b7280' }; // Default
};

const WeeksController = () => {
  // Track if user has manually switched tabs
  const userSwitchedTab = useRef(false);
  const [activeWeek, setActiveWeek] = useState<string>(`week${CURRENT_WEEK_NUMBER}`);
  const [episodes, setEpisodes] = useState<Episode[]>([]);
  const [previousWeekEpisodes, setPreviousWeekEpisodes] = useState<Episode[]>([]);
  const [loading, setLoading] = useState(true);
  const [isTransitioning, setIsTransitioning] = useState(false);
  
  const currentWeek = WEEKS_DATA.find(week => week.id === activeWeek);

  // Smooth transition function for week changes
  const handleWeekChange = (newWeek: string) => {
    if (newWeek === activeWeek) return;
    userSwitchedTab.current = true;
    setIsTransitioning(true);
    setTimeout(() => {
      setActiveWeek(newWeek);
    }, 150); // Half of the transition duration
  };
  
  // Load episodes when activeWeek changes
  // Helper to get the last week with episodes (before or including current)
  const getLastWeekWithEpisodes = async (): Promise<string> => {
    for (let i = CURRENT_WEEK_NUMBER; i >= 1; i--) {
      const week = WEEKS_DATA.find(w => w.id === `week${i}`);
      if (week) {
        try {
          const response = await fetch(`/${week.dataFile}`);
          if (response.ok) {
            const data = await response.json();
            if (Array.isArray(data) && data.filter((ep: any) => ep.rating > 0).length > 0) {
              return week.id;
            }
          }
        } catch {}
      }
    }
    return `week${CURRENT_WEEK_NUMBER}`;
  };

  // Main effect: load episodes and auto-switch tab if needed
  useEffect(() => {
    const loadWeekEpisodes = async () => {
      setLoading(true);
      try {
        const currentWeekData = WEEKS_DATA.find(week => week.id === activeWeek);
        if (currentWeekData) {
          // Load current week data
          const response = await fetch(`/${currentWeekData.dataFile}`);
          let filteredData: Episode[] = [];
          if (response.ok) {
            const data = await response.json();
            filteredData = data.filter((episode: Episode) => episode.rating > 0);
            setEpisodes(filteredData);
          } else {
            // Fallback to default episodes_data.json if week-specific file doesn't exist
            const fallbackResponse = await fetch('/episodes_data.json');
            const fallbackData = await fallbackResponse.json();
            filteredData = fallbackData.filter((episode: Episode) => episode.rating > 0);
            setEpisodes(filteredData);
          }

          // --- Auto-switch logic ---
          // Only auto-switch if user hasn't manually switched tabs
          if (!userSwitchedTab.current) {
            const isCurrentWeek = currentWeekData.isCurrentWeek;
            if (isCurrentWeek && filteredData.length === 0) {
              // Find last week with episodes
              const lastWithEpisodes = await getLastWeekWithEpisodes();
              if (lastWithEpisodes !== activeWeek) {
                setActiveWeek(lastWithEpisodes);
                return; // Wait for next effect
              }
            }
            if (isCurrentWeek && filteredData.length > 0 && activeWeek !== `week${CURRENT_WEEK_NUMBER}`) {
              setActiveWeek(`week${CURRENT_WEEK_NUMBER}`);
              return;
            }
          }

          // Load previous week data for comparison
          const currentWeekIndex = WEEKS_DATA.findIndex(week => week.id === activeWeek);
          if (currentWeekIndex > 0) {
            const previousWeekData = WEEKS_DATA[currentWeekIndex - 1];
            try {
              const prevResponse = await fetch(`/${previousWeekData.dataFile}`);
              if (prevResponse.ok) {
                const prevData = await prevResponse.json();
                const filteredPrevData = prevData.filter((episode: Episode) => episode.rating > 0);
                setPreviousWeekEpisodes(filteredPrevData);
              } else {
                setPreviousWeekEpisodes([]);
              }
            } catch (error) {
              setPreviousWeekEpisodes([]);
            }
          } else {
            setPreviousWeekEpisodes([]);
          }
        }
      } catch (error) {
        try {
          const fallbackResponse = await fetch('/episodes_data.json');
          const fallbackData = await fallbackResponse.json();
          const filteredFallbackData = fallbackData.filter((episode: Episode) => episode.rating > 0);
          setEpisodes(filteredFallbackData);
        } catch (fallbackError) {}
      } finally {
        setLoading(false);
        setTimeout(() => {
          setIsTransitioning(false);
        }, 150);
      }
    };
    loadWeekEpisodes();
  }, [activeWeek]);

  const firstPlaceImage = episodes.length > 0 ? episodes[0].anime_image_url : null;

  if (loading) {
    return (
      <main className="container mx-auto px-4 pt-8 pb-8 min-h-screen">
        <div className="text-center">Loading {currentWeek?.label}...</div>
      </main>
    );
  }

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
          Top Anime Episodes
        </h1>
        <p className="text-center mb-8 text-sm period-subtitle period-transition">
          {currentWeek ? getFormattedPeriod(currentWeek, currentWeek.isCurrentWeek) : 'Loading period...'}
        </p>
        
        {/* Week tabs */}
        <div className="flex justify-center mb-8">
          <div className="flex space-x-2 theme-card rounded-lg p-1">
            {WEEKS_DATA.map(week => (
              <button
                key={week.id}
                onClick={() => handleWeekChange(week.id)}
                className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                  activeWeek === week.id 
                    ? 'theme-rank' 
                    : 'theme-nav-link'
                }`}
              >
                {week.label}
              </button>
            ))}
          </div>
        </div>

        {episodes.length === 0 ? (
          <BlankState 
            weekNumber={currentWeek ? parseInt(currentWeek.id.replace('week', '')) : 1}
            weekPeriod={currentWeek ? currentWeek.title.replace(/^Week \d+ - /, '') : 'Loading...'}
            isCurrentWeek={currentWeek ? currentWeek.isCurrentWeek : false}
          />
        ) : (
          <div className={`grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6 content-grid ${isTransitioning ? 'loading' : ''}`}>
            {episodes.map((episode, index) => {
              const rank = index + 1;
              const positionChange = calculatePositionChange(episode, rank, previousWeekEpisodes);
              return (
                <EpisodeCard 
                  key={`${activeWeek}-${index}`} 
                  episode={episode} 
                  rank={rank}
                  positionChange={positionChange}
                />
              );
            })}
          </div>
        )}
      </div>
    </main>
  );
};

export default WeeksController;