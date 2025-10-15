import fs from 'fs';
import path from 'path';
import EpisodeCard from './components/EpisodeCard';

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

async function getEpisodes(): Promise<Episode[]> {
  const filePath = path.join(process.cwd(), 'public', 'episodes_data.json');
  const jsonData = fs.readFileSync(filePath, 'utf-8');
  return JSON.parse(jsonData);
}

export default async function Home() {
  const episodes = await getEpisodes();
  
  // Filter out episodes with rating 0 (not yet released episodes)
  const filteredEpisodes = episodes.filter(episode => episode.rating > 0);

  return (
    <main className="container mx-auto px-4 py-8">
      <h1 className="text-4xl font-bold text-center mb-8 text-white">Top Anime Episodes</h1>
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
        {filteredEpisodes.map((episode, index) => (
          <EpisodeCard key={index} episode={episode} rank={index + 1} />
        ))}
      </div>
    </main>
  );
}

