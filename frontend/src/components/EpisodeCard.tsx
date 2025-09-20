interface EpisodeCardProps {
  ranking: number;
  animeTitle: string;
  episodeNumber: string;
  episodeTitle: string;
  score: number;
  imageUrl: string;
  animeUrl: string;
  cardClass: string;
  rankBgColor: string;
  rankTextColor: string;
  scoreColor: string;
}

export default function EpisodeCard({
  ranking,
  animeTitle,
  episodeNumber,
  episodeTitle,
  score,
  imageUrl,
  animeUrl,
  cardClass,
  rankBgColor,
  rankTextColor,
  scoreColor,
}: EpisodeCardProps) {
  const episodeInfo = `E${episodeNumber}${episodeTitle && episodeTitle !== "Unknown" ? ` - ${episodeTitle}` : ""}`;

  return (
    <a href={`${animeUrl}/episode`} target="_blank" rel="noopener" style={{ textDecoration: 'none', color: 'inherit', display: 'contents' }}>
      <div className={`episode-card ${cardClass}`}>
        <div className="rank-section" style={{ backgroundColor: rankBgColor, color: rankTextColor }}>
          {ranking}
        </div>
        <div className="episode-content">
          <div className="episode-info-container">
            <h2 className="episode-title" style={{ color: rankBgColor }}>{animeTitle}</h2>
            <p className="episode-info">{episodeInfo}</p>
          </div>
          <div className="episode-image" style={{ backgroundImage: `url('${imageUrl}')` }}></div>
          <div className="episode-gradient"></div>
        </div>
        <div className="score-section">
          <p className="score-label">Score</p>
          <p className="score-value" style={{ color: scoreColor }}>{score.toFixed(2)}</p>
        </div>
      </div>
    </a>
  );
}
