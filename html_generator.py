from scraper_utils import get_ranking_colors

def generate_html_page(top_episodes, start_date, end_date):
    """Gera a página HTML completa com os episódios ranqueados"""
    
    # Carrega CSS
    with open('styles.css', 'r', encoding='utf-8') as f:
        css_content = f.read()
    
    # Carrega JavaScript
    with open('script.js', 'r', encoding='utf-8') as f:
        js_content = f.read()
    
    colors = get_ranking_colors()
    
    html = f"""<!doctype html>
<html lang="pt-BR">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="description" content="Top 50 Anime Episodes da Semana">
    <title>Top 50 Anime Episodes da Semana</title>
    <style>{css_content}</style>
  </head>
  <body>
    <div class="header">
      <div class="logo">
        <img src="assets/logo_transparent.png" alt="Top 10 Animes Logo" style="width: 100px; height: 100px;">
      </div>
      <div class="header-content">
        <h1 class="header-title">TOP 50 ANIME EPISODES <span class="header-subtitle">DA SEMANA</span></h1>
        <p class="header-date">{start_date.strftime('%d/%m/%Y').upper()} - {end_date.strftime('%d/%m/%Y').upper()}</p>
      </div>
    </div>
    
    <div class="main">"""

    for i, ep in enumerate(top_episodes, 1):
        # Determine colors based on rank
        if i == 1:
            rank_color = colors[1]
            score_color = colors[1]["bg"]
            card_class = "first"
        elif i in [2, 3]:
            rank_color = colors[2]
            score_color = colors[2]["bg"]
            card_class = "other"
        else:
            rank_color = colors["other"]
            score_color = colors["other"]["bg"]
            card_class = "other"
        
        anime_title = ep.get("anime_title", "Título não disponível")
        episode_num = ep.get("episode_number", "?")
        episode_title = ep.get("episode_title", "Episódio")
        score = ep.get("score", 0)
        img_url = ep.get("image", "")
        anime_url = ep.get("url", "").rstrip("/") + "/episode"
        
        # Create episode info text
        episode_info = f"S01 E{episode_num}"
        if episode_title and episode_title != "Unknown":
            episode_info += f" - {episode_title}"
        
        # Apply color to episode title based on rank
        title_color = rank_color["bg"]
        
        html += f"""
      <a href="{anime_url}" target="_blank" style="text-decoration: none; color: inherit;">
        <div class="episode-card {card_class}">
          <div class="rank-section" style="background-color: {rank_color['bg']}; color: {rank_color['text']};">
            {i}
          </div>
          <div class="episode-content">
            <div class="episode-info-container">
              <h2 class="episode-title" style="color: {title_color};">{anime_title}</h2>
              <p class="episode-info">{episode_info}</p>
            </div>
            <div class="episode-image" style="background-image: url('{img_url}');"></div>
            <div class="episode-gradient"></div>
          </div>
          <div class="score-section">
            <p class="score-label">Score</p>
            <p class="score-value" style="color: {score_color};">{score:.2f}</p>
          </div>
        </div>
      </a>"""

    html += f"""
    </div>
    
    <div class="footer">
      <p class="footer-text">Average score from 0 to 5 obtained from:</p>
      <div class="footer-logo">
        <img src="assets/MAL_logo.png" alt="MyAnimeList Logo" style="width: 200px; height: auto;">
      </div>
    </div>
    
    <!-- Fixed buttons -->
    <div class="fixed-buttons">
      <a href="#" id="scrollToTop" class="scroll-to-top">
        ↑
      </a>
      <a href="https://www.instagram.com/top10_animes" target="_blank" rel="noopener noreferrer" class="instagram-button">
        <img src="https://uxwing.com/wp-content/themes/uxwing/download/brands-and-social-media/instagram-white-icon.png" alt="Instagram" style="width: 30px; height: 30px;">
      </a>
    </div>
    
    <script>{js_content}</script>
  </body>
</html>"""
    
    return html

def generate_template_html():
    """Gera template HTML básico para customização"""
    return """<!doctype html>
<html lang="pt-BR">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="description" content="Top 50 Anime Episodes da Semana">
    <title>Top 50 Anime Episodes da Semana</title>
    <link rel="stylesheet" href="styles.css">
  </head>
  <body>
    <div class="header">
      <div class="logo">
        <img src="assets/logo_transparent.png" alt="Top 10 Animes Logo">
      </div>
      <div class="header-content">
        <h1 class="header-title">TOP 50 ANIME EPISODES <span class="header-subtitle">DA SEMANA</span></h1>
        <p class="header-date">[DATA_PERIODO]</p>
      </div>
    </div>
    
    <div class="main" id="episodes-container">
      <!-- Episódios serão inseridos aqui via JavaScript -->
    </div>
    
    <div class="footer">
      <p class="footer-text">Average score from 0 to 5 obtained from:</p>
      <div class="footer-logo">
        <img src="assets/MAL_logo.png" alt="MyAnimeList Logo">
      </div>
    </div>
    
    <!-- Fixed buttons -->
    <div class="fixed-buttons">
      <a href="#" id="scrollToTop" class="scroll-to-top">↑</a>
      <a href="https://www.instagram.com/top10_animes" target="_blank" rel="noopener noreferrer" class="instagram-button">
        <img src="https://uxwing.com/wp-content/themes/uxwing/download/brands-and-social-media/instagram-white-icon.png" alt="Instagram">
      </a>
    </div>
    
    <script src="script.js"></script>
  </body>
</html>"""
