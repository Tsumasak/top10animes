"""
VERSÃO SUPER OTIMIZADA - Busca apenas animes atualmente em exibição
Funciona em 30-60 segundos ao invés de minutos
"""

import json
import time
from datetime import datetime, timedelta, date
from jikan_api import make_jikan_request, _get_safe_title, _create_anime_slug

def get_config():
    """Carrega a configuração do arquivo JSON."""
    with open('config.json', 'r') as f:
        return json.load(f)

def get_currently_airing_animes():
    """Busca apenas animes que estão sendo exibidos AGORA - muito mais rápido!"""
    print("🚀 MODO RÁPIDO: Buscando apenas animes em exibição atual...")
    
    all_animes = []
    page = 1
    
    while len(all_animes) < 50:  # Máximo 50 animes para ser super rápido
        print(f"📄 Página {page}...")
        
        data = make_jikan_request("seasons/now", {
            "page": page,
            "limit": 25,
            "filter": "tv"
        })
        
        if not data or 'data' not in data or not data['data']:
            break
            
        page_animes = data['data']
        
        # Filtrar apenas animes populares
        filtered = [
            anime for anime in page_animes 
            if anime.get('members', 0) >= 20000 and
               (anime.get('score') or 0) >= 6.5
        ]
        
        all_animes.extend(filtered)
        
        if not data.get('pagination', {}).get('has_next_page', False):
            break
            
        page += 1
        
        if len(all_animes) >= 50:
            break
    
    # Pegar apenas os top 30 por popularidade
    all_animes = sorted(all_animes, 
                       key=lambda x: x.get('members', 0), 
                       reverse=True)[:30]
    
    print(f"✅ {len(all_animes)} animes em exibição encontrados")
    return all_animes

def get_anime_episodes_fast(anime_id, anime_title=""):
    """Versão otimizada para buscar episódios."""
    print(f"  📺 {anime_title[:40]}...")
    
    # Buscar apenas primeira página de episódios
    data = make_jikan_request(f"anime/{anime_id}/episodes", {"page": 1})
    
    if not data or 'data' not in data:
        return []
    
    episodes = data['data']
    print(f"    ✅ {len(episodes)} episódios")
    return episodes

def parse_episode_date(date_str):
    """Parse da data de episódio."""
    if not date_str:
        return None
        
    try:
        # Formato: "2024-10-12T15:30:00+00:00"
        if 'T' in date_str:
            date_part = date_str.split('T')[0]
            return datetime.strptime(date_part, '%Y-%m-%d').date()
        else:
            return datetime.strptime(date_str, '%Y-%m-%d').date()
    except:
        return None

def calculate_episode_score_fast(episode, anime_info):
    """Cálculo rápido de score."""
    # Score base do anime
    anime_score = anime_info.get('score', 6.0)
    base_score = anime_score * 0.85
    
    # Bônus por popularidade
    members = anime_info.get('members', 0)
    if members > 100000:
        base_score += 0.3
    elif members > 50000:
        base_score += 0.2
    elif members > 20000:
        base_score += 0.1
    
    # Bônus por episódios recentes
    episode_num = episode.get('mal_id', 1)
    if episode_num <= 3:  # Primeiros episódios
        base_score += 0.1
    
    return round(base_score, 2)

def get_anime_details_fast(anime_id):
    """Busca detalhes básicos do anime."""
    data = make_jikan_request(f"anime/{anime_id}")
    
    if not data or 'data' not in data:
        return None
        
    anime = data['data']
    
    return {
        'title': _get_safe_title(anime),
        'url': anime.get('url', ''),
        'image_url': anime.get('images', {}).get('jpg', {}).get('image_url', ''),
        'score': anime.get('score') or 6.0,
        'members': anime.get('members', 0),
        'rank': anime.get('rank', 0),
        'genres': [g.get('name', '') for g in anime.get('genres', [])],
        'studios': [s.get('name', '') for s in anime.get('studios', [])]
    }

def get_top_episodes_fast(start_date, end_date, limit=50):
    """
    VERSÃO SUPER RÁPIDA - usa apenas animes em exibição atual.
    Executa em 30-60 segundos.
    """
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    
    print(f"🚀 MODO RÁPIDO - TOP EPISÓDIOS: {start_date} até {end_date}")
    print("="*60)
    
    # 1. Buscar apenas animes em exibição atual
    animes = get_currently_airing_animes()
    
    if not animes:
        print("❌ Nenhum anime em exibição encontrado!")
        return []
    
    # 2. Processar episódios rapidamente
    all_episodes = []
    
    for i, anime in enumerate(animes, 1):
        anime_id = anime['mal_id']
        anime_title = _get_safe_title(anime)
        
        print(f"[{i:2d}/{len(animes)}] {anime_title[:50]}...")
        
        try:
            # Buscar detalhes básicos
            anime_details = get_anime_details_fast(anime_id)
            if not anime_details:
                print("    ❌ Erro nos detalhes")
                continue
                
            # Buscar episódios
            episodes = get_anime_episodes_fast(anime_id, anime_title)
            
            valid_count = 0
            for episode in episodes:
                air_date_str = episode.get('aired')
                if not air_date_str:
                    continue
                    
                episode_date = parse_episode_date(air_date_str)
                if not episode_date:
                    continue
                
                # Verificar período
                if start_date <= episode_date <= end_date:
                    score = calculate_episode_score_fast(episode, anime_details)
                    
                    episode_info = {
                        'anime_title': anime_details['title'],
                        'anime_url': anime_details['url'],
                        'anime_image': anime_details['image_url'],
                        'episode_number': episode.get('mal_id', 0),
                        'episode_title': episode.get('title', 'Episode'),
                        'episode_url': episode.get('url', ''),
                        'score': score,
                        'airdate': episode_date,
                        'anime_score': anime_details['score'],
                        'anime_members': anime_details['members'],
                        'anime_rank': anime_details['rank'],
                        'genres': anime_details['genres'],
                        'studios': anime_details['studios'],
                        'slug': _create_anime_slug(anime_details['title'])
                    }
                    
                    all_episodes.append(episode_info)
                    valid_count += 1
            
            if valid_count > 0:
                print(f"    ✅ {valid_count} episódio(s) válido(s)")
            else:
                print(f"    ⏭️  Nenhum episódio no período")
                
        except Exception as e:
            print(f"    ❌ Erro: {e}")
            continue
    
    # 3. Ordenar e limitar
    if not all_episodes:
        print("\n❌ Nenhum episódio encontrado no período!")
        return []
    
    # Ordenar por score
    all_episodes.sort(key=lambda x: x['score'], reverse=True)
    
    # Limitar resultados
    final_episodes = all_episodes[:limit]
    
    print(f"\n🏆 TOP {len(final_episodes)} EPISÓDIOS SELECIONADOS")
    print("="*60)
    for i, ep in enumerate(final_episodes[:10], 1):
        title_short = ep['anime_title'][:40]
        ep_title_short = ep['episode_title'][:30]
        print(f"{i:2d}. {title_short} - EP{ep['episode_number']}")
        print(f"     '{ep_title_short}' - Score: {ep['score']}")
    
    if len(final_episodes) > 10:
        print(f"     ... e mais {len(final_episodes) - 10} episódios")
    
    return final_episodes

def save_episodes_data_fast(episodes, start_date, end_date):
    """Salva os dados dos episódios."""
    config = get_config()
    output_file = config['weekly_episodes']['data_file']
    
    # Salvar também no diretório do frontend
    frontend_file = f"frontend/public/{output_file}"
    
    # Preparar dados para salvar
    episodes_data = []
    for episode in episodes:
        episode_data = {
            'anime_title': episode['anime_title'],
            'anime_url': episode['anime_url'], 
            'anime_image': episode['anime_image'],
            'episode_number': episode['episode_number'],
            'episode_title': episode['episode_title'],
            'episode_url': episode['episode_url'],
            'score': episode['score'],
            'airdate': episode['airdate'].isoformat(),
            'anime_score': episode['anime_score'],
            'anime_members': episode['anime_members'],
            'anime_rank': episode['anime_rank'],
            'genres': episode['genres'],
            'studios': episode['studios'],
            'slug': episode['slug']
        }
        episodes_data.append(episode_data)
    
    # Salvar arquivo principal
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(episodes_data, f, ensure_ascii=False, indent=2)
    
    # Salvar também para o frontend
    try:
        with open(frontend_file, 'w', encoding='utf-8') as f:
            json.dump(episodes_data, f, ensure_ascii=False, indent=2)
    except:
        pass  # Não é crítico se não conseguir salvar no frontend
    
    print(f"💾 Dados salvos: {len(episodes)} episódios em '{output_file}'")

if __name__ == "__main__":
    # Teste rápido
    start_date = date(2024, 10, 6)
    end_date = date(2024, 10, 12)
    
    episodes = get_top_episodes_fast(start_date, end_date, limit=20)
    save_episodes_data_fast(episodes, start_date, end_date)