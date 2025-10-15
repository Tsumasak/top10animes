import React from 'react';
import BaseAnimeCard from './BaseAnimeCard';

interface AnticipatedAnimeCardProps {
  anime: {
    title: string;
    image_url: string;
    members: number;
    mal_url: string;
    season: string;
    year: number;
    demographics?: string[]; // New demographics array
    genres?: string[]; // New genres array
    themes?: string[]; // New themes array
  };
  rank: number; // Added rank prop
}

const AnticipatedAnimeCard: React.FC<AnticipatedAnimeCardProps> = ({ anime, rank }) => {
  const membersText = `${anime.members.toLocaleString()} Plan to Watch`;

  return (
    <BaseAnimeCard
      rank={rank}
      title={anime.title}
      subtitle="" // Remove season info as it's redundant now with demographics/genres/themes
      imageUrl={anime.image_url}
      linkUrl={anime.mal_url}
      bottomText={membersText}
      demographics={anime.demographics}
      genres={anime.genres}
      themes={anime.themes}
    />
  );
};

export default AnticipatedAnimeCard;