import React from 'react';
import BaseAnimeCard from './BaseAnimeCard';

interface EpisodeCardProps {
  episode: {
    anime_id: number;
    anime_title: string;
    title: string; // Formatted episode title (e.g., "EP 1 • Name of the episode")
    episode_number: number;
    rating: number;
    anime_image_url: string;
    episode_url: string; // Pre-calculated MAL episode URL
    anime_type: string; // e.g., "TV", "ONA"
    is_manual?: number; // 1 if manually added episode, 0 or undefined if from API
  };
  rank: number; // The rank of the episode in the list
}

const EpisodeCard: React.FC<EpisodeCardProps> = ({ episode, rank }) => {
  const ratingText = `Rating: ${episode.rating}`;
  
  // Remover completamente qualquer diferenciação visual - episódios manuais idênticos aos automáticos
  return (
    <BaseAnimeCard
      rank={rank}
      title={episode.anime_title}
      subtitle={episode.title}
      imageUrl={episode.anime_image_url}
      linkUrl={episode.episode_url}
      bottomText={ratingText}
      animeType={episode.anime_type}
    />
  );
};

export default EpisodeCard;
