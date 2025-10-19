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
  };
  rank: number;
}

const AnticipatedAnimeCard: React.FC<AnticipatedAnimeCardProps> = ({ anime, rank }) => {
  return (
    <BaseAnimeCard
      rank={rank}
      title={anime.title}
      subtitle={`${anime.season} ${anime.year}`}
      imageUrl={anime.image_url}
      linkUrl={anime.mal_url}
      bottomText={`${anime.members.toLocaleString()} Plan to Watch`}
      animeType="" // No anime type for anticipated
      demographics={[]}
      genres={[]}
      themes={[]}
    />
  );
};

export default AnticipatedAnimeCard;