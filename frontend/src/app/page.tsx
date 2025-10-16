import fs from 'fs';
import path from 'path';
import EpisodeCard from '@/components/EpisodeCard';

type Episode = {
  anime_id: number;
  anime_title: string;
  title: string; // Formatted episode title (e.g., "EP 1 • Name of the episode")
  episode_number: number;
  rating: number;
  anime_image_url: string;
  episode_url: string; // Pre-calculated MAL episode URL
  anime_type: string; // e.g., "TV", "ONA"
};

interface UpdateMetadata {
  last_updated: string;
  episodes_period: {
    start_date: string;
    end_date: string;
  };
  anticipated_update_date: string;
}

async function getEpisodes(): Promise<Episode[]> {
  const filePath = path.join(process.cwd(), 'public', 'episodes_data.json');
  const jsonData = fs.readFileSync(filePath, 'utf-8');
  return JSON.parse(jsonData);
}

async function getUpdateMetadata(): Promise<UpdateMetadata> {
  try {
    const filePath = path.join(process.cwd(), 'public', 'update_metadata.json');
    const jsonData = fs.readFileSync(filePath, 'utf-8');
    return JSON.parse(jsonData);
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

// Helper function to format aired period from metadata
function getAiredPeriod(metadata: UpdateMetadata): string {
  const formatDate = (dateStr: string) => {
    // Parse date string manually to avoid timezone issues
    const [year, month, day] = dateStr.split('-').map(Number);
    const date = new Date(year, month - 1, day); // month is 0-indexed in JS
    return date.toLocaleDateString('en-US', { 
      month: 'short', 
      day: 'numeric', 
      year: 'numeric' 
    });
  };
  
  const startDate = formatDate(metadata.episodes_period.start_date);
  const endDate = formatDate(metadata.episodes_period.end_date);
  
  return `Aired - ${startDate} to ${endDate}`;
}

export default async function Home() {
  const episodes = await getEpisodes();
  const metadata = await getUpdateMetadata();
  
  // Filter out episodes with rating 0 (not yet released episodes)
  const filteredEpisodes = episodes.filter(episode => episode.rating > 0);
  
  // Get the first place anime image for background
  const firstPlaceImage = filteredEpisodes.length > 0 ? filteredEpisodes[0].anime_image_url : null;
  
  // Get aired period for subtitle
  const airedPeriod = getAiredPeriod(metadata);

  return (
    <main 
      className={`container mx-auto px-4 pt-8 pb-8 min-h-screen ${firstPlaceImage ? 'dynamic-background' : ''}`}
      style={{
        background: firstPlaceImage ? 'transparent' : 'var(--background)',
        ...(firstPlaceImage && { '--bg-image': `url("${firstPlaceImage}")` } as React.CSSProperties)
      }}
    >
      <div className="dynamic-background-content">
        <h1 className="text-4xl font-bold text-center mb-2" style={{color: 'var(--foreground)'}}>Top Anime Episodes</h1>
        <p className="text-center mb-8 text-sm period-subtitle">{airedPeriod}</p>
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
          {filteredEpisodes.map((episode, index) => (
            <EpisodeCard key={index} episode={episode} rank={index + 1} />
          ))}
        </div>
      </div>
    </main>
  );
}

