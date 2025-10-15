"""
Sistema completo usando apenas JIKAN API - Atualização de Animes Esperados
Elimina completamente a necessidade de scraping
"""

import json
import time
from datetime import datetime, timedelta
from jikan_api import make_jikan_request, _get_safe_title, _create_anime_slug

def get_config():
    """Carrega a configuração do arquivo JSON."""
    with open('config.json', 'r') as f:
        return json.load(f)

def get_current_season():
    """Determina a temporada atual baseada na data."""
    today = datetime.now()
    month = today.month
    year = today.year
    
    if month in [12, 1, 2]:
        return year if month == 12 else year, "winter"
    elif month in [3, 4, 5]:
        return year, "spring" 
    elif month in [6, 7, 8]:
        return year, "summer"
    else:  # 9, 10, 11
        return year, "fall"

def get_upcoming_season():
    """Determina a próxima temporada baseada na data atual."""
    today = datetime.now()
    month = today.month
    year = today.year
    
    if month in [10, 11, 12]:
        return year + 1 if month == 12 else year, "winter" if month == 12 else "winter"
    elif month in [1, 2, 3]:
        return year, "spring"
    elif month in [4, 5, 6]:
        return year, "summer"
    else:  # 7, 8, 9
        return year, "fall"

def get_detailed_anime_info(anime_id):
    """Busca informações detalhadas de um anime específico."""
    print(f"  Buscando detalhes para anime ID: {anime_id}")
    
    data = make_jikan_request(f"anime/{anime_id}")
    if not data or 'data' not in data:
        return None
        
    anime = data['data']
    
    # Buscar estatísticas adicionais se disponível
    stats_data = make_jikan_request(f"anime/{anime_id}/statistics")
    stats = {}
    if stats_data and 'data' in stats_data:
        stats = stats_data['data']
    
    return {
        'mal_id': anime['mal_id'],
        'title': _get_safe_title(anime),
        'title_english': anime.get('title_english', ''),
        'title_japanese': anime.get('title_japanese', ''),
        'url': anime.get('url', ''),
        'image_url': anime['images']['jpg'].get('large_image_url', 
                    anime['images']['jpg'].get('image_url', '')),
        'trailer_url': anime.get('trailer', {}).get('url', ''),
        'synopsis': anime.get('synopsis', ''),
        'background': anime.get('background', ''),
        'type': anime.get('type', ''),
        'source': anime.get('source', ''),
        'episodes': anime.get('episodes'),
        'status': anime.get('status', ''),
        'airing': anime.get('airing', False),
        'duration': anime.get('duration', ''),
        'rating': anime.get('rating', ''),
        'score': anime.get('score', 0),
        'scored_by': anime.get('scored_by', 0),
        'rank': anime.get('rank'),
        'popularity': anime.get('popularity'),
        'members': anime.get('members', 0),
        'favorites': anime.get('favorites', 0),
        'year': anime.get('year'),
        'season': anime.get('season'),
        'broadcast': anime.get('broadcast', {}),
        'producers': [producer['name'] for producer in anime.get('producers', [])],
        'licensors': [licensor['name'] for licensor in anime.get('licensors', [])],
        'studios': [studio['name'] for studio in anime.get('studios', [])],
        'genres': [genre['name'] for genre in anime.get('genres', [])],
        'themes': [theme['name'] for theme in anime.get('themes', [])],
        'demographics': [demo['name'] for demo in anime.get('demographics', [])],
        'relations': anime.get('relations', []),
        'watching': stats.get('watching', 0),
        'completed': stats.get('completed', 0),
        'on_hold': stats.get('on_hold', 0),
        'dropped': stats.get('dropped', 0),
        'plan_to_watch': stats.get('plan_to_watch', 0),
        'total_stats': stats.get('total', 0)
    }

def get_anticipated_animes_full():
    """
    Busca animes mais esperados com informações completas via JIKAN API.
    Combina dados de temporadas atuais e futuras.
    """
    config = get_config()
    anticipated_config = config.get('anticipated_animes', {})
    
    # Configurações
    max_animes = anticipated_config.get('max_animes', 50)
    min_members = anticipated_config.get('min_members', 1000)
    
    print(f"Buscando top {max_animes} animes mais esperados...")
    print(f"Critério mínimo: {min_members:,} membros")
    
    all_animes = []
    
    # 1. Buscar da temporada atual e próximas
    current_year, current_season = get_current_season()
    upcoming_year, upcoming_season = get_upcoming_season()
    
    seasons_to_check = [
        (current_year, current_season),
        (upcoming_year, upcoming_season)
    ]
    
    # Adicionar próxima temporada se diferente
    if (upcoming_year, upcoming_season) not in seasons_to_check:
        seasons_to_check.append((upcoming_year, upcoming_season))
    
    print(f"Verificando temporadas: {seasons_to_check}")
    
    for year, season in seasons_to_check:
        print(f"\n🔍 Buscando animes de {season.title()} {year}...")
        
        page = 1
        season_animes = []
        
        while len(season_animes) < 100:  # Limitar busca por temporada
            data = make_jikan_request(f"seasons/{year}/{season}", {
                "page": page, 
                "limit": 25,
                "filter": "tv"  # Focar em séries TV
            })
            
            if not data or 'data' not in data or not data['data']:
                break
                
            page_animes = data['data']
            season_animes.extend(page_animes)
            
            # Verificar se há próxima página
            if not data.get('pagination', {}).get('has_next_page', False):
                break
                
            page += 1
        
        print(f"  Encontrados {len(season_animes)} animes em {season.title()} {year}")
        all_animes.extend(season_animes)
    
    # 2. Buscar animes mais populares/esperados adicionais
    print(f"\n🔍 Buscando animes mais populares...")
    
    # Top animes por membros/popularidade
    top_data = make_jikan_request("top/anime", {
        "filter": "airing",
        "limit": 25
    })
    
    if top_data and 'data' in top_data:
        all_animes.extend(top_data['data'])
        print(f"  Adicionados {len(top_data['data'])} animes do ranking top")
    
    # 3. Filtrar e processar animes
    print(f"\n📊 Processando {len(all_animes)} animes encontrados...")
    
    processed_animes = []
    seen_ids = set()
    
    for anime in all_animes:
        anime_id = anime['mal_id']
        
        # Evitar duplicatas
        if anime_id in seen_ids:
            continue
        seen_ids.add(anime_id)
        
        # Filtros básicos
        members_count = anime.get('members', 0)
        if members_count < min_members:
            continue
            
        # Filtrar animes já finalizados há muito tempo
        status = anime.get('status', '')
        if status == 'Finished Airing':
            # Verificar se é recente (último ano)
            year = anime.get('year')
            if year and year < datetime.now().year - 1:
                continue
        
        # Buscar informações detalhadas
        detailed_info = get_detailed_anime_info(anime_id)
        if not detailed_info:
            continue
            
        # Calcular "expectativa" baseada em múltiplos fatores
        expectation_score = calculate_expectation_score(detailed_info)
        detailed_info['expectation_score'] = expectation_score
        
        processed_animes.append(detailed_info)
        
        print(f"  ✅ {detailed_info['title'][:50]}... (Membros: {members_count:,}, Score: {expectation_score:.2f})")
    
    # 4. Ordenar por expectativa e aplicar limite
    processed_animes.sort(key=lambda x: x['expectation_score'], reverse=True)
    top_animes = processed_animes[:max_animes]
    
    # 5. Adicionar rankings
    for i, anime in enumerate(top_animes, 1):
        anime['ranking'] = i
        anime['members_display'] = f"{anime['members']:,}"
    
    print(f"\n🎯 Selecionados top {len(top_animes)} animes mais esperados!")
    return top_animes

def calculate_expectation_score(anime_info):
    """
    Calcula um score de expectativa baseado em múltiplos fatores.
    """
    score = 0
    
    # Fator 1: Número de membros (peso alto)
    members = anime_info.get('members', 0)
    score += min(members / 1000000 * 30, 30)  # Máximo 30 pontos
    
    # Fator 2: Score atual (se disponível)
    mal_score = anime_info.get('score', 0)
    if mal_score > 0:
        score += mal_score * 3  # Máximo ~27 pontos
    
    # Fator 3: Status (mais esperado se ainda não começou)
    status = anime_info.get('status', '')
    if status == 'Not yet aired':
        score += 15
    elif status == 'Currently Airing':
        score += 10
    
    # Fator 4: Popularidade (ranking)
    popularity = anime_info.get('popularity', float('inf'))
    if popularity and popularity != float('inf'):
        score += max(20 - (popularity / 1000), 0)  # Máximo 20 pontos
    
    # Fator 5: Número de pessoas planejando assistir
    plan_to_watch = anime_info.get('plan_to_watch', 0)
    score += min(plan_to_watch / 100000 * 10, 10)  # Máximo 10 pontos
    
    # Fator 6: Estúdios famosos (bônus)
    famous_studios = [
        'Mappa', 'Wit Studio', 'Studio Ghibli', 'Madhouse', 'Bones',
        'Production I.G', 'Toei Animation', 'Pierrot', 'A-1 Pictures',
        'Sunrise', 'Shaft', 'KyoAni', 'Trigger', 'Ufotable'
    ]
    
    studios = anime_info.get('studios', [])
    for studio in studios:
        if any(famous in studio for famous in famous_studios):
            score += 5
            break
    
    # Fator 7: Sequências de animes populares (bônus)
    title = anime_info.get('title', '').lower()
    if any(word in title for word in ['season', 'part', '2nd', '3rd', 'final']):
        score += 8
    
    return round(score, 2)

def save_anticipated_animes_data(animes_data, output_path="frontend/public/"):
    """Salva os dados dos animes esperados em JSON com informações completas."""
    import os
    
    # Garantir que o diretório existe
    os.makedirs(output_path, exist_ok=True)
    
    output_data = {
        'generated_date': datetime.now().isoformat(),
        'total_animes': len(animes_data),
        'update_source': 'JIKAN_API_FULL',
        'criteria': {
            'min_members': get_config().get('anticipated_animes', {}).get('min_members', 1000),
            'max_results': get_config().get('anticipated_animes', {}).get('max_animes', 50),
            'calculation_method': 'expectation_score'
        },
        'animes': animes_data
    }
    
    output_file = os.path.join(output_path, 'anticipated_animes_data.json')
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2, default=str)
    
    print(f"💾 Dados salvos: {len(animes_data)} animes em '{output_file}'")
    return output_data

def main():
    """Função principal para atualizar animes esperados."""
    print("🚀 ATUALIZADOR DE ANIMES MAIS ESPERADOS - 100% JIKAN API")
    print("=" * 80)
    
    start_time = datetime.now()
    
    try:
        # Buscar animes esperados
        animes_data = get_anticipated_animes_full()
        
        if not animes_data:
            print("❌ Nenhum anime foi encontrado!")
            return
        
        # Salvar dados
        save_anticipated_animes_data(animes_data)
        
        # Estatísticas
        end_time = datetime.now()
        duration = end_time - start_time
        
        print("\n" + "=" * 80)
        print("📈 ESTATÍSTICAS DA ATUALIZAÇÃO")
        print("=" * 80)
        print(f"🎯 Animes processados: {len(animes_data)}")
        print(f"⏱️  Tempo total: {duration}")
        print(f"📅 Última atualização: {end_time.strftime('%d/%m/%Y às %H:%M')}")
        
        # Top 10 preview
        print(f"\n🏆 TOP 10 ANIMES MAIS ESPERADOS:")
        for i, anime in enumerate(animes_data[:10], 1):
            print(f"{i:2d}. {anime['title'][:60]}...")
            print(f"     Score: {anime['expectation_score']:.1f} | Membros: {anime['members_display']}")
        
        print("\n✅ Atualização concluída com sucesso!")
        
    except Exception as e:
        print(f"\n❌ Erro durante a atualização: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()