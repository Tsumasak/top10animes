'use client';

import { useState, useEffect } from 'react';
import EpisodeCard from './EpisodeCard';

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

interface WeekData {
  id: string;
  title: string;
  period: string;
  label: string;
  dataFile: string;
}

const WEEKS_DATA: WeekData[] = [
  {
    id: 'week1',
    title: 'Week 1 - Sep 29 - Oct 5, 2025',
    period: 'Aired - Sep 29, 2025 to Oct 5, 2025',
    label: 'Week 1',
    dataFile: 'week1_episodes_data.json'
  },
  {
    id: 'week2', 
    title: 'Week 2 - Oct 6-12, 2025',
    period: 'Aired - Oct 6, 2025 to Oct 12, 2025',
    label: 'Week 2',
    dataFile: 'week2_episodes_data.json'
  },
  {
    id: 'week3',
    title: 'Week 3 - Oct 13-19, 2025', 
    period: 'Airing - Oct 13, 2025 to Oct 19, 2025',
    label: 'Week 3',
    dataFile: 'week3_episodes_data.json'
  }
];

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

// Trend indicators system (kept for backward compatibility with old trend system)
const getTrendIndicator = (rank: number, weekId: string) => {
  if (weekId === 'week3') {
    // Week 3 (Current week) - Hot trends
    if (rank <= 3) return { symbol: '🔥', color: '#ef4444' }; // Red for hot
    if (rank <= 6) return { symbol: '⬆️', color: '#22c55e' }; // Green for rising
    if (rank <= 10) return { symbol: '=', color: '#6b7280' }; // Gray for stable
    return { symbol: '⬇️', color: '#f97316' }; // Orange for falling
  }
  
  if (weekId === 'week2') {
    // Week 2 - Trending indicators
    if (rank <= 5) return { symbol: '🆕', color: '#3b82f6' }; // Blue for new
    if (rank <= 10) return { symbol: '⬆️', color: '#22c55e' }; // Green for rising
    return { symbol: '=', color: '#6b7280' }; // Gray for stable
  }
  
  if (weekId === 'week1') {
    // Week 1 - Historical data (oldest)
    if (rank <= 5) return { symbol: '⬆️', color: '#22c55e' }; // Green for good performance
    return { symbol: '=', color: '#6b7280' }; // Gray for average
  }
  
  return { symbol: '=', color: '#6b7280' }; // Default
};

export default function WeeksController() {
  const [activeWeek, setActiveWeek] = useState('week3'); // Start with current week
  const [episodes, setEpisodes] = useState<Episode[]>([]);
  const [previousWeekEpisodes, setPreviousWeekEpisodes] = useState<Episode[]>([]);
  const [loading, setLoading] = useState(true);
  const [isTransitioning, setIsTransitioning] = useState(false);
  
  const currentWeek = WEEKS_DATA.find(week => week.id === activeWeek);

  // Smooth transition function for week changes
  const handleWeekChange = (newWeek: string) => {
    if (newWeek === activeWeek) return;
    
    setIsTransitioning(true);
    setTimeout(() => {
      setActiveWeek(newWeek);
    }, 150); // Half of the transition duration
  };
  
  // Load episodes when activeWeek changes
  useEffect(() => {
    const loadWeekEpisodes = async () => {
      setLoading(true);
      try {
        const currentWeekData = WEEKS_DATA.find(week => week.id === activeWeek);
        if (currentWeekData) {
          // Load current week data
          const response = await fetch(`/${currentWeekData.dataFile}`);
          if (response.ok) {
            const data = await response.json();
            const filteredData = data.filter((episode: Episode) => episode.rating > 0);
            setEpisodes(filteredData);
          } else {
            // Fallback to default episodes_data.json if week-specific file doesn't exist
            const fallbackResponse = await fetch('/episodes_data.json');
            const fallbackData = await fallbackResponse.json();
            const filteredFallbackData = fallbackData.filter((episode: Episode) => episode.rating > 0);
            setEpisodes(filteredFallbackData);
          }

          // Load previous week data for comparison
          const currentWeekIndex = WEEKS_DATA.findIndex(week => week.id === activeWeek);
          console.log(`Current week: ${activeWeek}, index: ${currentWeekIndex}`);
          
          if (currentWeekIndex > 0) {
            const previousWeekData = WEEKS_DATA[currentWeekIndex - 1];
            console.log(`Loading previous week data: ${previousWeekData.dataFile}`);
            try {
              const prevResponse = await fetch(`/${previousWeekData.dataFile}`);
              if (prevResponse.ok) {
                const prevData = await prevResponse.json();
                const filteredPrevData = prevData.filter((episode: Episode) => episode.rating > 0);
                console.log(`Previous week episodes loaded: ${filteredPrevData.length} episodes`);
                console.log('First few previous episodes:', filteredPrevData.slice(0, 3));
                setPreviousWeekEpisodes(filteredPrevData);
              } else {
                console.log('Failed to load previous week data');
                setPreviousWeekEpisodes([]);
              }
            } catch (error) {
              console.error('Error loading previous week data:', error);
              setPreviousWeekEpisodes([]);
            }
          } else {
            // No previous week (this is week 1)
            console.log('No previous week (Week 1)');
            setPreviousWeekEpisodes([]);
          }
        }
      } catch (error) {
        console.error('Error loading episodes for week:', activeWeek, error);
        // Fallback to default episodes_data.json
        try {
          const fallbackResponse = await fetch('/episodes_data.json');
          const fallbackData = await fallbackResponse.json();
          const filteredFallbackData = fallbackData.filter((episode: Episode) => episode.rating > 0);
          setEpisodes(filteredFallbackData);
        } catch (fallbackError) {
          console.error('Error loading fallback episodes:', fallbackError);
        }
      } finally {
        setLoading(false);
        // Reset transition state after loading completes
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
          {currentWeek ? getFormattedPeriod(currentWeek, activeWeek === 'week3') : 'Loading period...'}
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
      </div>
    </main>
  );
}