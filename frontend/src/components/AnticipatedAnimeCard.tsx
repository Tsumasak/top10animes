interface AnticipatedAnimeCardProps {
  ranking: number;
  animeTitle: string;
  membersDisplay: string;
  imageUrl: string;
  animeUrl: string;
  cardClass: string;
  rankBgColor: string;
  rankTextColor: string;
  membersColor: string;
}

export default function AnticipatedAnimeCard({
  ranking,
  animeTitle,
  membersDisplay,
  imageUrl,
  animeUrl,
  cardClass,
  rankBgColor,
  rankTextColor,
  membersColor,
}: AnticipatedAnimeCardProps) {
  return (
    <a href={animeUrl} target="_blank" rel="noopener" style={{ textDecoration: 'none', color: 'inherit', display: 'contents' }}>
      <div className={`episode-card ${cardClass}`}>
        <div className="rank-section" style={{ backgroundColor: rankBgColor, color: rankTextColor }}>
          {ranking}
        </div>
        <div className="episode-content">
          <div className="episode-info-container">
            <h2 className="episode-title" style={{ color: rankBgColor }}>{animeTitle}</h2>
          </div>
          <div className="episode-image" style={{ backgroundImage: `url('${imageUrl}')` }}></div>
          <div className="episode-gradient"></div>
        </div>
        <div className="score-section">
          <p className="score-label">Plan to Watch</p>
          <p className="score-value" style={{ color: membersColor }}>{membersDisplay}</p>
        </div>
      </div>
    </a>
  );
}
