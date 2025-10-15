import requests
import json
from datetime import datetime, timedelta
import time
import re
from scraper_utils import debug_print

def _create_anime_slug(title):
    """Cria um slug URL-friendly a partir do título do anime."""
    if not title:
        return "unknown"
    # Substitui espaços por underscores e remove caracteres especiais
    slug = re.sub(r'[^a-zA-Z0-9_ ]', '', str(title))
    slug = slug.replace(' ', '_')
    return slug

def _get_safe_title(anime_data):
    """Obtém o título do anime de forma segura."""
    # Tenta título em inglês primeiro, depois japonês, depois título padrão
    title = anime_data.get('title_english')
    if not title:
        title = anime_data.get('title_japanese')
    if not title:
        title = anime_data.get('title', 'Unknown Title')
    return str(title) if title else 'Unknown Title'

def get_config():
    """Carrega a configuração do arquivo JSON."""
    with open('config.json', 'r') as f:
        return json.load(f)

def save_config(config_data):
    """Salva os dados de configuração no arquivo JSON."""
    with open('config.json', 'w') as f:
        json.dump(config_data, f, indent=2)

def make_jikan_request(endpoint, params=None):
    """
    Faz uma requisição à API Jikan, respeitando o rate limit.
    """
    base_url = "https://api.jikan.moe/v4"
    url = f"{base_url}/{endpoint}"
    
    try:
        response = requests.get(url, params=params or {})
        
        # Rate limiting - Jikan recomenda 3 requests por segundo máximo
        time.sleep(0.5)
        
        if response.status_code == 429:  # Too Many Requests
            print("Rate limit atingido. Aguardando...")
            time.sleep(5)
            response = requests.get(url, params=params or {})
        
        response.raise_for_status()
        return response.json()
        
    except requests.exceptions.RequestException as e:
        print(f"Erro na requisição à API Jikan para {url}: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"Detalhes do erro: {e.response.text}")
        return None

def get_anime_details(anime_id):
    """Busca detalhes completos de um anime específico via API Jikan."""
    debug_print(f"Buscando detalhes para o anime ID: {anime_id}", 3)
    
    data = make_jikan_request(f"anime/{anime_id}")
    if data and 'data' in data:
        anime = data['data']
        return {
            'id': anime['mal_id'],
            'title': _get_safe_title(anime),
            'title_japanese': anime.get('title_japanese', ''),
            'score': anime.get('score', 0),
            'scored_by': anime.get('scored_by', 0),
            'members': anime.get('members', 0),
            'favorites': anime.get('favorites', 0),
            'image_url': anime['images']['jpg'].get('large_image_url', anime['images']['jpg'].get('image_url')),
            'synopsis': anime.get('synopsis', ''),
            'genres': [genre['name'] for genre in anime.get('genres', [])],
            'studios': [studio['name'] for studio in anime.get('studios', [])],
            'year': anime.get('year'),
            'season': anime.get('season'),
            'episodes': anime.get('episodes'),
            'duration': anime.get('duration'),
            'rating': anime.get('rating'),
            'status': anime.get('status'),
            'airing': anime.get('airing', False),
            'url': anime.get('url')
        }
    return None

def get_seasonal_animes_jikan(year, season, limit=100, min_members=20000):
    """
    Busca animes de uma temporada específica usando a API Jikan.
    """
    print(f"Buscando animes da temporada {season.capitalize()} {year} via API Jikan...")
    
    all_animes = []
    page = 1
    
    while len(all_animes) < limit:
        data = make_jikan_request(f"seasons/{year}/{season}", {"page": page, "limit": 25})
        
        if not data or 'data' not in data or not data['data']:
            break
            
        page_animes = data['data']
        
        for anime in page_animes:
            members_count = anime.get('members', 0)
            
            if members_count >= min_members:
                # Obtém o título de forma segura
                title = _get_safe_title(anime)
                anime_slug = _create_anime_slug(title)
                
                formatted_anime = {
                    'title': title,
                    'url': anime.get('url', f"https://myanimelist.net/anime/{anime['mal_id']}/{anime_slug}"),
                    'image': anime['images']['jpg'].get('large_image_url', anime['images']['jpg'].get('image_url')),
                    'members': members_count,
                    'score': anime.get('score', 0),
                    'scored_by': anime.get('scored_by', 0),
                    'episodes': anime.get('episodes', 0),
                    'status': anime.get('status', ''),
                    'airing': anime.get('airing', False),
                    'genres': [genre['name'] for genre in anime.get('genres', [])],
                    'studios': [studio['name'] for studio in anime.get('studios', [])]
                }
                
                all_animes.append(formatted_anime)
        
        # Verifica se há mais páginas
        if not data.get('pagination', {}).get('has_next_page', False):
            break
            
        page += 1
        
        if len(all_animes) >= limit:
            break
    
    # Ordena por número de membros e limita
    all_animes = sorted(all_animes, key=lambda x: x['members'], reverse=True)[:limit]
    
    print(f"Total de animes filtrados para o ranking semanal: {len(all_animes)}")
    return all_animes

def get_anticipated_animes():
    """
    Busca os animes mais esperados de uma temporada específica usando a API Jikan.
    """
    config = get_config()
    anticipated_config = config['anticipated_animes']
    season_str = anticipated_config['season'] # Ex: "Fall 2025"
    limit = anticipated_config['max_animes']
    min_members = anticipated_config['min_members']

    # Extrai ano e estação da string (Ex: "Fall 2025" -> 2025, "fall")
    try:
        parts = season_str.split(' ')
        season_name = parts[0].lower()
        year = int(parts[1])
    except (IndexError, ValueError):
        print(f"Erro: Formato de temporada inválido em config.json: {season_str}. Esperado 'Estação Ano'.")
        return []

    debug_print(f"DEBUG: Buscando animes para Ano: {year}, Estação: {season_name}", 1)
    print(f"Buscando animes mais esperados da temporada {season_name.capitalize()} {year} via API Jikan...")
    
    all_animes = []
    page = 1
    
    # Busca todos os animes da temporada
    while True:
        data = make_jikan_request(f"seasons/{year}/{season_name}", {"page": page, "limit": 25})
        
        if not data or 'data' not in data or not data['data']:
            break
            
        page_animes = data['data']
        
        for anime in page_animes:
            members_count = anime.get('members', 0)
            
            if members_count >= min_members:
                # Obtém o título de forma segura
                title = _get_safe_title(anime)
                anime_slug = _create_anime_slug(title)
                
                formatted_anime = {
                    'ranking': 0,  # Será atribuído após ordenação
                    'title': title,
                    'url': anime.get('url', f"https://myanimelist.net/anime/{anime['mal_id']}/{anime_slug}"),
                    'image': anime['images']['jpg'].get('large_image_url', anime['images']['jpg'].get('image_url')),
                    'members_count': members_count,
                    'members_display': f"{members_count:,}",
                    'score': anime.get('score', 0),
                    'scored_by': anime.get('scored_by', 0),
                    'episodes': anime.get('episodes', 0),
                    'status': anime.get('status', ''),
                    'airing': anime.get('airing', False),
                    'genres': [genre['name'] for genre in anime.get('genres', [])],
                    'studios': [studio['name'] for studio in anime.get('studios', [])]
                }
                
                all_animes.append(formatted_anime)
        
        # Verifica se há mais páginas
        if not data.get('pagination', {}).get('has_next_page', False):
            break
            
        page += 1
    
    # Ordena os animes por número de membros (decrescente) e aplica o limite
    all_animes = sorted(all_animes, key=lambda x: x['members_count'], reverse=True)[:limit]
    
    # Atribui o ranking final
    for i, anime in enumerate(all_animes):
        anime['ranking'] = i + 1

    print(f"Encontrados {len(all_animes)} animes mais esperados para a temporada {season_name.capitalize()} {year}.")
    return all_animes

def get_top_anime_by_score(limit=50, min_score=7.0):
    """
    Busca os animes com melhor score usando a API Jikan.
    """
    print(f"Buscando top {limit} animes por score via API Jikan...")
    
    all_animes = []
    page = 1
    
    while len(all_animes) < limit:
        data = make_jikan_request("top/anime", {"page": page, "limit": 25})
        
        if not data or 'data' not in data or not data['data']:
            break
            
        page_animes = data['data']
        
        for anime in page_animes:
            score = anime.get('score', 0)
            
            if score >= min_score:
                title = _get_safe_title(anime)
                anime_slug = _create_anime_slug(title)
                
                formatted_anime = {
                    'ranking': anime.get('rank', 0),
                    'title': title,
                    'url': anime.get('url', f"https://myanimelist.net/anime/{anime['mal_id']}/{anime_slug}"),
                    'image': anime['images']['jpg'].get('large_image_url', anime['images']['jpg'].get('image_url')),
                    'score': score,
                    'scored_by': anime.get('scored_by', 0),
                    'members': anime.get('members', 0),
                    'episodes': anime.get('episodes', 0),
                    'type': anime.get('type', ''),
                    'status': anime.get('status', ''),
                    'genres': [genre['name'] for genre in anime.get('genres', [])],
                    'studios': [studio['name'] for studio in anime.get('studios', [])]
                }
                
                all_animes.append(formatted_anime)
        
        # Verifica se há mais páginas
        if not data.get('pagination', {}).get('has_next_page', False):
            break
            
        page += 1
        
        if len(all_animes) >= limit:
            break
    
    print(f"Encontrados {len(all_animes)} animes top por score.")
    return all_animes[:limit]

def search_anime(query, limit=10):
    """
    Busca animes por nome usando a API Jikan.
    """
    print(f"Buscando animes com query: '{query}'...")
    
    data = make_jikan_request("anime", {"q": query, "limit": limit, "order_by": "score", "sort": "desc"})
    
    if not data or 'data' not in data:
        return []
    
    results = []
    for anime in data['data']:
        title = _get_safe_title(anime)
        anime_slug = _create_anime_slug(title)
        
        result = {
            'id': anime['mal_id'],
            'title': title,
            'url': anime.get('url', f"https://myanimelist.net/anime/{anime['mal_id']}/{anime_slug}"),
            'image': anime['images']['jpg'].get('large_image_url', anime['images']['jpg'].get('image_url')),
            'score': anime.get('score', 0),
            'scored_by': anime.get('scored_by', 0),
            'members': anime.get('members', 0),
            'episodes': anime.get('episodes', 0),
            'type': anime.get('type', ''),
            'status': anime.get('status', ''),
            'year': anime.get('year'),
            'season': anime.get('season'),
            'genres': [genre['name'] for genre in anime.get('genres', [])],
            'studios': [studio['name'] for studio in anime.get('studios', [])]
        }
        
        results.append(result)
    
    print(f"Encontrados {len(results)} resultados para '{query}'.")
    return results