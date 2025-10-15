import fs from 'fs';
import path from 'path';
import EpisodeCard from '@/components/EpisodeCard';
import ClientLayout from '@/components/ClientLayout';

interface EpisodeData {
  anime_title: string;
  episode_number: number;
  episode_title: string;
  score: number;
  anime_image: string;
  anime_url: string;
  episode_url?: string | null;
  airdate: string;
  anime_score: number;
  anime_members: number;
  anime_rank: number;
  genres: string[];
  studios: string[];
  slug: string;
}

interface EpisodesJsonData {
  generated_at: string;
  start_date?: string;
  end_date?: string;
  episodes: EpisodeData[];
}

// Function to get ranking colors (replicated from Python)
function getRankingColors() {
  return {
    1: { bg: "#88FE70", text: "#212121" }, // Green
    2: { bg: "#FE70A9", text: "#212121" }, // Pink
    3: { bg: "#FE70A9", text: "#212121" }, // Pink
    other: { bg: "#FECB70", text: "#212121" } // Yellow
  };
}

export default function WeeklyEpisodesPage() {
  let episodesData: EpisodesJsonData = { generated_at: "", episodes: [] };
  try {
    const filePath = path.join(process.cwd(), 'public', 'episodes_data.json');
    const fileContents = fs.readFileSync(filePath, 'utf8');
    const rawData = JSON.parse(fileContents);
    
    // Handle both formats: array and object
    if (Array.isArray(rawData)) {
      episodesData = {
        generated_at: new Date().toISOString(),
        episodes: rawData
      };
    } else {
      episodesData = rawData;
    }
    
    // Ensure episodes array exists
    if (!episodesData.episodes) {
      episodesData.episodes = [];
    }
  } catch (error) {
    console.error("Error reading episodes_data.json:", error);
    episodesData = { generated_at: "", episodes: [] };
  }

  const colors = getRankingColors();

  const formatDate = (dateString: string | undefined) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    const day = String(date.getUTCDate()).padStart(2, '0');
    const month = String(date.getUTCMonth() + 1).padStart(2, '0');
    const year = date.getUTCFullYear();
    return `${day}/${month}/${year}`;
  };

  const periodInfo = episodesData.start_date && episodesData.end_date
    ? `${formatDate(episodesData.start_date)} - ${formatDate(episodesData.end_date)}`
    : 'Período não definido';

  return (
    <ClientLayout periodInfo={periodInfo}>
      {episodesData.episodes && episodesData.episodes.length > 0 ? episodesData.episodes.map((episode, index) => {
          const rank = index + 1;
          const isFirst = rank === 1;
          const isTop3 = rank <= 3;

          let rankBgColor = colors.other.bg;
          let rankTextColor = colors.other.text;
          let scoreColor = colors.other.bg;
          let cardClass = "other";

          if (isFirst) {
            rankBgColor = colors[1].bg;
            rankTextColor = colors[1].text;
            scoreColor = colors[1].bg;
            cardClass = "first";
          } else if (isTop3) {
            rankBgColor = colors[2].bg;
            rankTextColor = colors[2].text;
            scoreColor = colors[2].bg;
            cardClass = "other";
          }

          return (
            <EpisodeCard
              key={episode.anime_url + episode.episode_number} // Unique key
              ranking={rank}
              animeTitle={episode.anime_title}
              episodeNumber={episode.episode_number.toString()}
              episodeTitle={episode.episode_title}
              score={episode.score}
              imageUrl={episode.anime_image}
              animeUrl={episode.anime_url}
              cardClass={cardClass}
              rankBgColor={rankBgColor}
              rankTextColor={rankTextColor}
              scoreColor={scoreColor}
            />
          );
        }) : (
          <div className="text-center text-gray-500 mt-8">
            <p>Nenhum episódio encontrado.</p>
            <p>Execute o sistema backend para gerar os dados.</p>
          </div>
        )}
    </ClientLayout>
  );
}