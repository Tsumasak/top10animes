import fs from 'fs';
import path from 'path';
import AnticipatedAnimeCard from '@/components/AnticipatedAnimeCard';
import ClientLayout from '@/components/ClientLayout';

interface AnimeData {
  ranking: number;
  title: string;
  members_display: string;
  image: string;
  url: string;
}

interface AnticipatedJsonData {
  generated_date: string;
  season: string;
  total_animes: number;
  animes: AnimeData[];
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

export default function AnticipatedAnimesPage() {
  let animesData: AnticipatedJsonData = { generated_date: "", season: "", total_animes: 0, animes: [] };
  try {
    const filePath = path.join(process.cwd(), 'public', 'anticipated_animes_data.json');
    const fileContents = fs.readFileSync(filePath, 'utf8');
    animesData = JSON.parse(fileContents);
  } catch (error) {
    console.error("Error reading anticipated_animes_data.json:", error);
  }

  const colors = getRankingColors();

  return (
    <ClientLayout periodInfo={animesData.season.toUpperCase()} headerTitle="TOP 50 MOST ANTICIPATED ANIMES">
      {animesData.animes.map((anime) => {
          const rank = anime.ranking;
          const isFirst = rank === 1;
          const isTop3 = rank <= 3;

          let rankBgColor = colors.other.bg;
          let rankTextColor = colors.other.text;
          let membersColor = colors.other.bg;
          let cardClass = "other";

          if (isFirst) {
            rankBgColor = colors[1].bg;
            rankTextColor = colors[1].text;
            membersColor = colors[1].bg;
            cardClass = "first";
          } else if (isTop3) {
            rankBgColor = colors[2].bg;
            rankTextColor = colors[2].text;
            membersColor = colors[2].bg;
            cardClass = "other";
          }

          return (
            <AnticipatedAnimeCard
              key={anime.url} // Unique key
              ranking={rank}
              animeTitle={anime.title}
              membersDisplay={anime.members_display}
              imageUrl={anime.image}
              animeUrl={anime.url}
              cardClass={cardClass}
              rankBgColor={rankBgColor}
              rankTextColor={rankTextColor}
              membersColor={membersColor}
            />
          );
        })}
    </ClientLayout>
  );
}
