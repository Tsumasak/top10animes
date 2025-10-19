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
  };
  rank: number; // The rank of the episode in the list
  positionChange?: number; // Position change from previous week
}

const EpisodeCard: React.FC<EpisodeCardProps> = ({ episode, rank, positionChange }) => {
  // Generate anime URL by removing /episode/{number} from episode_url
  const animeUrl = episode.episode_url.replace(/\/episode\/\d+$/, '');
  
  return (
    <BaseAnimeCard
      rank={rank}
      title={episode.anime_title}
      subtitle={episode.title}
      imageUrl={episode.anime_image_url}
      linkUrl={animeUrl}
      bottomText={`★ ${episode.rating.toFixed(2)}`}
      animeType={episode.anime_type}
      positionChange={positionChange}
    />
  );
};

export default EpisodeCard;
