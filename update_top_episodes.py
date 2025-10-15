"""
Sistema completo usando apenas JIKAN API - Atualização de Top Episódios
Elimina completamente a necessidade de scraping
"""

import json
import time
from datetime import datetime, timedelta, date
from jikan_api import make_jikan_request, _get_safe_title, _create_anime_slug

def get_config():
    """Carrega a configuração do arquivo JSON."""
    with open('config.json', 'r') as f:
        return json.load(f)

def get_season_from_date(target_date):
    """Determina o ano e a estação a partir de uma data específica."""
    if isinstance(target_date, str):
        target_date = datetime.strptime(target_date, '%Y-%m-%d').date()
    elif isinstance(target_date, datetime):
        target_date = target_date.date()
    
    year = target_date.year
    month = target_date.month
    
    if month in [12, 1, 2]:
        season = "winter"
        # Se dezembro, é winter do próximo ano
        if month == 12:
            year += 1
    elif month in [3, 4, 5]:
        season = "spring"
    elif month in [6, 7, 8]:
        season = "summer" 
    else:  # 9, 10, 11
        season = "fall"
    
    return year, season

def get_anime_episodes_jikan(anime_id, anime_title=""):
    """Busca episódios de um anime via JIKAN API."""
    print(f"  📺 Buscando episódios para: {anime_title[:50]}...")
    
    all_episodes = []
    page = 1
    
    while True:
        data = make_jikan_request(f"anime/{anime_id}/episodes", {"page": page})
        
        if not data or 'data' not in data or not data['data']:
            break
            
        episodes = data['data']
        all_episodes.extend(episodes)
        
        # Verificar se há próxima página
        if not data.get('pagination', {}).get('has_next_page', False):
            break
            
        page += 1
        
        # Limitar para evitar muitas requisições
        if page > 10:  # Máximo 250 episódios (25 * 10)
            break
    
    print(f"    ✅ Encontrados {len(all_episodes)} episódios")
    return all_episodes

def parse_episode_date(date_str):
    """Converte string de data para objeto date."""
    if not date_str:
        return None
        
    try:
        # JIKAN retorna no formato ISO: "2024-10-12T00:00:00+00:00"
        if 'T' in date_str:
            date_str = date_str.split('T')[0]
        
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except:
        return None

def get_anime_details_for_episodes(anime_id):
    """Busca detalhes do anime necessários para os episódios."""
    data = make_jikan_request(f"anime/{anime_id}")
    
    if not data or 'data' not in data:
        return None
        
    anime = data['data']
    
    return {
        'mal_id': anime['mal_id'],
        'title': _get_safe_title(anime),
        'url': anime.get('url', ''),
        'image_url': anime['images']['jpg'].get('large_image_url', 
                    anime['images']['jpg'].get('image_url', '')),
        'score': anime.get('score', 0),
        'members': anime.get('members', 0),
        'popularity': anime.get('popularity'),
        'rank': anime.get('rank'),
        'status': anime.get('status', ''),
        'airing': anime.get('airing', False),
        'genres': [genre['name'] for genre in anime.get('genres', [])],
        'studios': [studio['name'] for studio in anime.get('studios', [])]
    }

def get_seasonal_animes_for_episodes(start_date, end_date):
    """Busca animes das temporadas relevantes para o período especificado."""
    print(f"🔍 Buscando animes para período: {start_date} até {end_date}")
    
    # Determinar temporadas a verificar
    seasons_to_check = set()
    
    # Adicionar temporada da data início
    year1, season1 = get_season_from_date(start_date)
    seasons_to_check.add((year1, season1))
    
    # Adicionar temporada da data fim
    year2, season2 = get_season_from_date(end_date)
    seasons_to_check.add((year2, season2))
    
    # Adicionar temporadas anteriores para capturar animes contínuos
    for year, season in list(seasons_to_check):
        # Adicionar temporada anterior
        if season == "winter":
            seasons_to_check.add((year - 1, "fall"))
        elif season == "spring":
            seasons_to_check.add((year, "winter"))
        elif season == "summer":
            seasons_to_check.add((year, "spring"))
        else:  # fall
            seasons_to_check.add((year, "summer"))
    
    print(f"📅 Temporadas a verificar: {sorted(seasons_to_check)}")
    
    all_animes = []
    
    for year, season in sorted(seasons_to_check):
        print(f"\n🎯 Buscando animes de {season.title()} {year}...")
        
        page = 1
        season_animes = []
        
        while len(season_animes) < 30:  # OTIMIZAÇÃO: Reduzir drasticamente para 30 animes por temporada
            data = make_jikan_request(f"seasons/{year}/{season}", {
                "page": page, 
                "limit": 25,
                "filter": "tv"
            })
            
            if not data or 'data' not in data or not data['data']:
                break
                
            page_animes = data['data']
            
            # OTIMIZAÇÃO: Filtrar apenas animes com base em popularidade
            filtered_animes = [
                anime for anime in page_animes 
                if anime.get('members', 0) >= 25000  # Filtro de popularidade ajustado
            ]
            
            season_animes.extend(filtered_animes)
            all_animes.extend(filtered_animes)
            
            # OTIMIZAÇÃO: Parar se já temos animes suficientes ou não há mais páginas
            if len(season_animes) >= 30 or not data.get('pagination', {}).get('has_next_page', False):
                break
                
            page += 1
        
        print(f"  ✅ {len(season_animes)} animes encontrados em {season.title()} {year}")
    
    # Remover duplicatas
    unique_animes = {}
    for anime in all_animes:
        anime_id = anime['mal_id']
        if anime_id not in unique_animes:
            unique_animes[anime_id] = anime

    final_animes = list(unique_animes.values())
    
    # OTIMIZAÇÃO: Limitar a 40 animes no total para velocidade
    if len(final_animes) > 40:
        # Ordenar por score + membros e pegar os top 40
        final_animes = sorted(final_animes, 
                            key=lambda x: (x.get('score', 0) * x.get('members', 0)), 
                            reverse=True)[:40]
        print(f"\n📊 Total de animes únicos: {len(unique_animes)} (limitado a {len(final_animes)} para otimização)")
    else:
        print(f"\n📊 Total de animes únicos: {len(final_animes)}")

    return final_animes

def calculate_episode_score(episode_data, anime_info):
    """
    Calcula um score estimado para o episódio baseado em múltiplos fatores.
    Como não temos scores diretos dos episódios via JIKAN, 
    usamos uma combinação de fatores do anime e do episódio.
    """
    base_score = 0
    
    # Fator 1: Score do anime (peso alto)
    anime_score = anime_info.get('score', 0)
    if anime_score > 0:
        base_score += anime_score * 0.8  # Usar 80% do score do anime
    
    # Fator 2: Popularidade do anime
    members = anime_info.get('members', 0)
    if members > 0:
        # Normalizar membros para um valor entre 0 e 2
        member_bonus = min(members / 1000000 * 2, 2)
        base_score += member_bonus
    
    # Fator 3: Ranking do anime
    rank = anime_info.get('rank')
    if rank:
        # Animes top 100 ganham bônus
        if rank <= 100:
            base_score += 0.5
        elif rank <= 500:
            base_score += 0.3
    
    # Fator 4: Status de exibição
    if anime_info.get('airing', False):
        base_score += 0.3  # Bônus para animes em exibição
    
    # Fator 5: Gêneros populares
    genres = anime_info.get('genres', [])
    popular_genres = ['Action', 'Adventure', 'Drama', 'Fantasy', 'Thriller']
    genre_bonus = sum(0.1 for genre in genres if genre in popular_genres)
    base_score += min(genre_bonus, 0.5)
    
    # Fator 6: Estúdios famosos
    studios = anime_info.get('studios', [])
    famous_studios = ['Mappa', 'Wit Studio', 'Madhouse', 'Bones', 'Ufotable', 'Studio Ghibli']
    if any(studio in famous_studios for studio in studios):
        base_score += 0.2
    
    # Fator 7: Tipo de episódio (finais de temporada tendem a ser melhores)
    episode_num = episode_data.get('mal_id', 0)
    title = episode_data.get('title', '').lower()
    
    # Bônus para episódios finais ou especiais
    if any(word in title for word in ['final', 'finale', 'end', 'climax']):
        base_score += 0.4
    elif any(word in title for word in ['special', 'ova', 'movie']):
        base_score += 0.3
    
    # Garantir que o score está em uma faixa realista (1.0 - 10.0)
    final_score = max(1.0, min(10.0, base_score))
    
    # Adicionar uma pequena variação aleatória baseada no ID do episódio
    # para evitar empates exatos
    import hashlib
    variation = (int(hashlib.md5(str(episode_num).encode()).hexdigest()[:4], 16) % 100) / 1000
    final_score += variation
    
    return round(final_score, 2)

def get_top_episodes_jikan(start_date, end_date, limit=50):
    """
    Busca os melhores episódios do período usando apenas JIKAN API.
    VERSÃO OTIMIZADA para velocidade.
    """
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    
    print(f"🎬 BUSCANDO TOP EPISÓDIOS - {start_date} até {end_date}")
    print("=" * 80)
    
    # 1. Buscar animes das temporadas relevantes
    animes = get_seasonal_animes_for_episodes(start_date, end_date)
    
    if not animes:
        print("❌ Nenhum anime encontrado para o período!")
        return []
    
    # 2. Processar episódios de cada anime
    all_episodes = []
    
    print(f"\n📺 Processando episódios de {len(animes)} animes...")
    
    for i, anime in enumerate(animes, 1):
        anime_id = anime['mal_id']
        anime_title = _get_safe_title(anime)
        
        print(f"\n[{i:3d}/{len(animes)}] {anime_title[:50]}...")
        
        try:
            # Buscar detalhes do anime
            anime_details = get_anime_details_for_episodes(anime_id)
            if not anime_details:
                continue
            
            # Buscar episódios
            episodes = get_anime_episodes_jikan(anime_id, anime_title)
            
            # Filtrar episódios por data
            valid_episodes = []
            for episode in episodes:
                air_date_str = episode.get('aired')
                if not air_date_str:
                    continue
                    
                episode_date = parse_episode_date(air_date_str)
                if not episode_date:
                    continue
                
                # Verificar se está no período
                if start_date <= episode_date <= end_date:
                    # Calcular score estimado
                    estimated_score = calculate_episode_score(episode, anime_details)
                    
                    episode_info = {
                        'anime_title': anime_details['title'],
                        'anime_url': anime_details['url'],
                        'anime_image': anime_details['image_url'],
                        'episode_number': episode.get('mal_id', 0),
                        'episode_title': episode.get('title', 'Episode'),
                        'episode_url': episode.get('url', ''),
                        'score': estimated_score,
                        'airdate': episode_date,
                        'anime_score': anime_details['score'],
                        'anime_members': anime_details['members'],
                        'anime_rank': anime_details['rank'],
                        'genres': anime_details['genres'],
                        'studios': anime_details['studios'],
                        'filler': episode.get('filler', False),
                        'recap': episode.get('recap', False)
                    }
                    
                    valid_episodes.append(episode_info)
            
            if valid_episodes:
                all_episodes.extend(valid_episodes)
                print(f"    ✅ {len(valid_episodes)} episódios válidos encontrados")
            else:
                print(f"    ⏭️  Nenhum episódio no período")
                
        except Exception as e:
            print(f"    ❌ Erro processando {anime_title}: {e}")
            continue
    
    # 3. Ordenar e limitar
    if not all_episodes:
        print("❌ Nenhum episódio encontrado no período!")
        return []
    
    # Filtrar episódios filler e recap (opcional)
    quality_episodes = [
        ep for ep in all_episodes 
        if not ep.get('filler', False) and not ep.get('recap', False)
    ]
    
    if not quality_episodes:
        quality_episodes = all_episodes  # Fallback se todos forem filler
    
    # Ordenar por score
    top_episodes = sorted(quality_episodes, key=lambda x: x['score'], reverse=True)[:limit]
    
    print(f"\n🏆 TOP {len(top_episodes)} EPISÓDIOS SELECIONADOS")
    print("=" * 80)
    
    for i, ep in enumerate(top_episodes[:10], 1):
        print(f"{i:2d}. {ep['anime_title']} - EP{ep['episode_number']}")
        print(f"     '{ep['episode_title'][:50]}' - Score: {ep['score']:.2f}")
    
    return top_episodes

def save_episodes_data(episodes, start_date, end_date, output_path="frontend/public/"):
    """Salva os dados dos episódios em JSON."""
    import os
    
    # Garantir que o diretório existe
    os.makedirs(output_path, exist_ok=True)
    
    output_data = {
        'generated_at': datetime.now().isoformat(),
        'start_date': str(start_date),
        'end_date': str(end_date),
        'total_episodes': len(episodes),
        'update_source': 'JIKAN_API_ONLY',
        'scoring_method': 'calculated_from_anime_data',
        'episodes': episodes
    }
    
    output_file = os.path.join(output_path, 'episodes_data.json')
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2, default=str)
    
    print(f"💾 Dados salvos: {len(episodes)} episódios em '{output_file}'")
    return output_data

def main():
    """Função principal para atualizar episódios."""
    print("🚀 ATUALIZADOR DE TOP EPISÓDIOS - 100% JIKAN API")
    print("=" * 80)
    
    start_time = datetime.now()
    
    try:
        # Solicitar período ao usuário
        print("📅 Definir período para busca de episódios:")
        
        while True:
            start_str = input("Data início (YYYY-MM-DD): ")
            end_str = input("Data fim (YYYY-MM-DD): ")
            
            try:
                start_date = datetime.strptime(start_str, '%Y-%m-%d').date()
                end_date = datetime.strptime(end_str, '%Y-%m-%d').date()
                
                if start_date > end_date:
                    print("❌ Data início não pode ser posterior à data fim!")
                    continue
                    
                break
                
            except ValueError:
                print("❌ Formato inválido! Use YYYY-MM-DD (ex: 2024-10-01)")
        
        # Buscar episódios
        episodes = get_top_episodes_jikan(start_date, end_date, limit=50)
        
        if not episodes:
            print("❌ Nenhum episódio encontrado!")
            return
        
        # Salvar dados
        save_episodes_data(episodes, start_date, end_date)
        
        # Estatísticas
        end_time = datetime.now()
        duration = end_time - start_time
        
        print("\n" + "=" * 80)
        print("📈 ESTATÍSTICAS DA ATUALIZAÇÃO")
        print("=" * 80)
        print(f"🎬 Episódios processados: {len(episodes)}")
        print(f"⏱️  Tempo total: {duration}")
        print(f"📅 Período analisado: {start_date} até {end_date}")
        print(f"📅 Última atualização: {end_time.strftime('%d/%m/%Y às %H:%M')}")
        
        # Estatísticas por anime
        animes_count = len(set(ep['anime_title'] for ep in episodes))
        print(f"📺 Animes únicos: {animes_count}")
        
        # Score médio
        avg_score = sum(ep['score'] for ep in episodes) / len(episodes)
        print(f"📊 Score médio: {avg_score:.2f}")
        
        print("\n✅ Atualização concluída com sucesso!")
        
    except Exception as e:
        print(f"\n❌ Erro durante a atualização: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()