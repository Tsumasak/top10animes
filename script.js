// Scroll to top functionality
const scrollToTopBtn = document.getElementById('scrollToTop');

window.addEventListener('scroll', function() {
  if (window.pageYOffset > 300) {
    scrollToTopBtn.classList.add('visible');
  } else {
    scrollToTopBtn.classList.remove('visible');
  }
});

scrollToTopBtn.addEventListener('click', function(e) {
  e.preventDefault();
  window.scrollTo({
    top: 0,
    behavior: 'smooth'
  });
});

// Função para carregar episódios dinamicamente (caso use JSON)
async function loadEpisodesFromJSON() {
  try {
    const response = await fetch('episodes_data.json');
    const data = await response.json();
    return data.episodes;
  } catch (error) {
    console.error('Erro ao carregar dados dos episódios:', error);
    return [];
  }
}

// Função para gerar cards de episódios dinamicamente
function generateEpisodeCard(episode, index) {
  const colors = {
    1: { bg: "#88FE70", text: "#212121" },  // Green
    2: { bg: "#FE70A9", text: "#212121" },  // Pink  
    3: { bg: "#FE70A9", text: "#212121" },  // Pink
    other: { bg: "#FECB70", text: "#212121" }  // Yellow
  };
  
  let rankColor, scoreColor, cardClass;
  
  if (index === 1) {
    rankColor = colors[1];
    scoreColor = colors[1].bg;
    cardClass = "first";
  } else if (index === 2 || index === 3) {
    rankColor = colors[2];
    scoreColor = colors[2].bg;
    cardClass = "other";
  } else {
    rankColor = colors.other;
    scoreColor = colors.other.bg;
    cardClass = "other";
  }
  
  const animeTitle = episode.anime_title || "Título não disponível";
  const episodeNum = episode.episode_number || "?";
  const episodeTitle = episode.episode_title || "Episódio";
  const score = episode.score || 0;
  const imgUrl = episode.image || "";
  const animeUrl = (episode.url || "").replace(/\/$/, "") + "/episode";
  
  let episodeInfo = `S01 E${episodeNum}`;
  if (episodeTitle && episodeTitle !== "Unknown") {
    episodeInfo += ` - ${episodeTitle}`;
  }
  
  const titleColor = rankColor.bg;
  
  return `
    <a href="${animeUrl}" target="_blank" style="text-decoration: none; color: inherit;">
      <div class="episode-card ${cardClass}">
        <div class="rank-section" style="background-color: ${rankColor.bg}; color: ${rankColor.text};">
          ${index}
        </div>
        <div class="episode-content">
          <div class="episode-info-container">
            <h2 class="episode-title" style="color: ${titleColor};">${animeTitle}</h2>
            <p class="episode-info">${episodeInfo}</p>
          </div>
          <div class="episode-image" style="background-image: url('${imgUrl}');"></div>
          <div class="episode-gradient"></div>
        </div>
        <div class="score-section">
          <p class="score-label">Score</p>
          <p class="score-value" style="color: ${scoreColor};">${score.toFixed(2)}</p>
        </div>
      </div>
    </a>
  `;
}

// Função para renderizar todos os episódios
function renderEpisodes(episodes) {
  const container = document.getElementById('episodes-container');
  if (!container) return;
  
  const episodesHTML = episodes
    .slice(0, 50) // Top 50
    .map((episode, index) => generateEpisodeCard(episode, index + 1))
    .join('');
  
  container.innerHTML = episodesHTML;
}

// Função para atualizar período no header
function updateHeaderDate(startDate, endDate) {
  const headerDate = document.querySelector('.header-date');
  if (headerDate) {
    const formatDate = (date) => {
      return date.toLocaleDateString('pt-BR').toUpperCase();
    };
    headerDate.textContent = `${formatDate(startDate)} - ${formatDate(endDate)}`;
  }
}

// Inicialização quando o DOM estiver carregado
document.addEventListener('DOMContentLoaded', function() {
  // Se existir container para episódios, tentar carregar do JSON
  const episodesContainer = document.getElementById('episodes-container');
  if (episodesContainer) {
    loadEpisodesFromJSON().then(episodes => {
      if (episodes.length > 0) {
        renderEpisodes(episodes);
      }
    });
  }
  
  // Outras inicializações se necessário
  console.log('Top 50 Anime Episodes carregado com sucesso!');
});

// Função para filtrar episódios por score mínimo
function filterEpisodesByScore(episodes, minScore = 0) {
  return episodes
    .filter(ep => ep.score >= minScore)
    .sort((a, b) => b.score - a.score);
}

// Função para buscar episódios por nome do anime
function searchAnimeByTitle(episodes, searchTerm) {
  const term = searchTerm.toLowerCase();
  return episodes.filter(ep => 
    ep.anime_title.toLowerCase().includes(term)
  );
}

// Exportar funções para uso global (se necessário)
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    loadEpisodesFromJSON,
    generateEpisodeCard,
    renderEpisodes,
    filterEpisodesByScore,
    searchAnimeByTitle,
    updateHeaderDate
  };
}