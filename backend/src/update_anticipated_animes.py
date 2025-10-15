import sqlite3
import os
import time
import json
from jikan_api import get_season_anime, get_upcoming_anime, get_top_airing_anime, get_anime_full_details # Import get_anime_full_details
from database_setup import setup_database
import datetime # Import datetime

def print_log(message):
    """Print message to console with timestamp"""
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")

def write_log(log_file, message):
    """Write message to both log file and console"""
    print_log(message)
    log_file.write(f"{message}\n")
    log_file.flush()  # Ensure immediate write

# Helper to get current season and year
def get_current_season_and_year():
    now = datetime.datetime.now()
    month = now.month
    year = now.year

    season = ''
    if month >= 3 and month <= 5:
        season = 'spring'
    elif month >= 6 and month <= 8:
        season = 'summer'
    elif month >= 9 and month <= 11:
        season = 'fall'
    else: # December, January, February
        season = 'winter'
    return {'season': season, 'year': year}

# Helper to get next N seasons
def get_next_seasons(current_season: str, current_year: int, count: int):
    seasons_order = ['winter', 'spring', 'summer', 'fall']
    current_season_index = seasons_order.index(current_season)
    
    next_seasons = []
    year_adjust = 0
    for i in range(count):
        current_season_index += 1
        if current_season_index >= len(seasons_order):
            current_season_index = 0
            year_adjust += 1
        next_seasons.append({'season': seasons_order[current_season_index], 'year': current_year + year_adjust})
    return next_seasons

def update_anticipated_animes_data():
    print_log("🚀 Iniciando atualização dos animes mais antecipados...")
    
    setup_database() # Ensure tables exist
    print_log("✅ Database configurado")
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(os.path.dirname(script_dir), 'top10animes.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    print_log(f"📁 Conectado ao banco: {db_path}")

    log_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'anticipated_debug.log')

    with open(log_file_path, 'w', encoding='utf-8') as log_file:
        write_log(log_file, "📡 Buscando animes mais antecipados da API Jikan...")
        
        all_anticipated_animes = {} # Dictionary to store unique animes by mal_id

        # Determine current and next seasons
        current_season_info = get_current_season_and_year()
        next_two_seasons_info = get_next_seasons(current_season_info['season'], current_season_info['year'], 2)
        write_log(log_file, f"📅 Temporada atual: {current_season_info['season']} {current_season_info['year']}")
        next_seasons_str = [f"{s['season']} {s['year']}" for s in next_two_seasons_info]
        write_log(log_file, f"📅 Próximas temporadas: {next_seasons_str}")

        # Fetch current season's anime (from /seasons/{year}/{season}) - for current season only
        write_log(log_file, f"🔍 Buscando temporada atual: {current_season_info['season']} {current_season_info['year']}")
        current_upcoming_anime_data = get_season_anime(current_season_info['year'], current_season_info['season'])
        current_count = len(current_upcoming_anime_data['data'])
        write_log(log_file, f"✅ Encontrados {current_count} animes da temporada atual")
        
        for item in current_upcoming_anime_data['data']:
            all_anticipated_animes[item['mal_id']] = item # Overwrite if already fetched, ensuring latest data
        time.sleep(0.5)

        # Fetch next two seasons' anime
        for i, season_info in enumerate(next_two_seasons_info, 1):
            write_log(log_file, f"🔍 Buscando temporada futura {i}/2: {season_info['season']} {season_info['year']}")
            next_season_anime_data = get_season_anime(season_info['year'], season_info['season'])
            season_count = len(next_season_anime_data['data'])
            write_log(log_file, f"✅ Encontrados {season_count} animes para {season_info['season']} {season_info['year']}")
            
            for item in next_season_anime_data['data']:
                all_anticipated_animes[item['mal_id']] = item
            time.sleep(0.5)

        # Fetch all upcoming anime (for 'Later' category) - this is the /seasons/upcoming endpoint
        write_log(log_file, "🔍 Buscando animes 'Later' (upcoming)...")
        upcoming_anime_data = get_upcoming_anime()
        upcoming_count = len(upcoming_anime_data['data'])
        write_log(log_file, f"✅ Encontrados {upcoming_count} animes upcoming")
        
        for item in upcoming_anime_data['data']:
            all_anticipated_animes[item['mal_id']] = item # Overwrite if already fetched, ensuring latest data

        # Clear table before inserting
        write_log(log_file, "🗑️ Limpando tabela anticipated_animes...")
        c.execute("DELETE FROM anticipated_animes")
        conn.commit() # Explicitly commit the deletion
        
        total_animes = len(all_anticipated_animes)
        write_log(log_file, f"📊 Total de animes únicos coletados: {total_animes}")
        write_log(log_file, "🔄 Processando animes e filtrando por temporadas...")

        # Process and insert unique animes
        processed_count = 0
        skipped_count = 0
        inserted_count = 0
        
        for mal_id, item in all_anticipated_animes.items():
            processed_count += 1
            if processed_count % 10 == 0:  # Log a cada 10 animes
                write_log(log_file, f"⏳ Processados {processed_count}/{total_animes} animes...")
            # Determine season and year for 'Later' category
            item_season = item.get('season')
            item_year = item.get('year')
            
            # Get current and next two seasons for categorization
            current_season_info = get_current_season_and_year()
            next_two_seasons_info = get_next_seasons(current_season_info['season'], current_season_info['year'], 2)

            # SKIP ANIMES FROM PAST SEASONS (before current season)
            if item_season and item_year:
                # Check if this anime is from a past season
                if item_year < current_season_info['year']:
                    # Anime from previous year - skip it
                    log_file.write(f"⏭️ Pulando anime de ano passado: {item.get('title')} ({item_season} {item_year})\n")
                    skipped_count += 1
                    continue
                elif item_year == current_season_info['year']:
                    # Same year - check if season is before current
                    seasons_order = ['winter', 'spring', 'summer', 'fall']
                    current_season_idx = seasons_order.index(current_season_info['season'])
                    item_season_idx = seasons_order.index(item_season.lower())
                    
                    if item_season_idx < current_season_idx:
                        # Anime from earlier season in same year - skip it
                        log_file.write(f"⏭️ Pulando anime de temporada passada: {item.get('title')} ({item_season} {item_year})\n")
                        skipped_count += 1
                        continue

            is_specific_season = False
            if item_season and item_year:
                # Check if this anime belongs to current or next two seasons
                if (item_season.lower() == current_season_info['season'] and item_year == current_season_info['year']):
                    is_specific_season = True
                else:
                    for next_s in next_two_seasons_info:
                        if item_season.lower() == next_s['season'] and item_year == next_s['year']:
                            is_specific_season = True
                            break
            
            # Categorize anime by season  
            if not is_specific_season:
                # For animes not in current or next two seasons, categorize as 'Later'
                season_to_save = 'Later'
                year_to_save = None
            else:
                season_to_save = item_season
                year_to_save = item_year

            # Get English title, fallback to default
            anime_title = item.get('title_english')
            if not anime_title:
                anime_title = item.get('title')

            mal_url = item.get('url')

            # Get demographics, genres, and themes - try from current data first, then fetch details if needed
            demographics_names = []
            genres_names = []
            themes_names = []

            # Check if demographics, genres, and themes are available in current item data
            if 'demographics' in item and item['demographics']:
                demographics_names = [demo['name'] for demo in item['demographics']]
            
            if 'genres' in item and item['genres']:
                genres_names = [genre['name'] for genre in item['genres']]
            
            if 'themes' in item and item['themes']:
                themes_names = [theme['name'] for theme in item['themes']]

            # If missing any data, fetch full details
            if not demographics_names or not genres_names or not themes_names:
                try:
                    log_file.write(f"Fetching full details for anime ID {item.get('mal_id')}...\n")
                    full_details = get_anime_full_details(item.get('mal_id'))
                    anime_data = full_details.get('data', {})
                    
                    if not demographics_names and 'demographics' in anime_data:
                        demographics_names = [demo['name'] for demo in anime_data['demographics']]
                    
                    if not genres_names and 'genres' in anime_data:
                        genres_names = [genre['name'] for genre in anime_data['genres']]
                    
                    if not themes_names and 'themes' in anime_data:
                        themes_names = [theme['name'] for theme in anime_data['themes']]
                
                except Exception as e:
                    log_file.write(f"Error fetching full details for {item.get('mal_id')}: {e}\n")

            # Convert to JSON strings for storage (empty list if none)
            demographics_json = json.dumps(demographics_names) if demographics_names else json.dumps([])
            genres_json = json.dumps(genres_names) if genres_names else json.dumps([])
            themes_json = json.dumps(themes_names) if themes_names else json.dumps([])

            log_file.write(f"✅ Inserindo: ID={item.get('mal_id')}, Title={anime_title}, Season={season_to_save}, Year={year_to_save}, Demographics={demographics_names}, Genres={genres_names[:2]}, Themes={themes_names[:2]}\n")

            c.execute("INSERT INTO anticipated_animes (id, title, image_url, members, season, year, mal_url, demographics, genres, themes) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                      (item.get('mal_id'), anime_title, item['images']['jpg']['large_image_url'], item.get('members', 0), season_to_save, year_to_save, mal_url, demographics_json, genres_json, themes_json))
            inserted_count += 1
            time.sleep(0.1) # Be respectful to the Jikan API

        conn.commit()
        conn.close()
        
        write_log(log_file, f"📊 Estatísticas finais:")
        write_log(log_file, f"   - Total processados: {processed_count}")
        write_log(log_file, f"   - Animes pulados: {skipped_count}")
        write_log(log_file, f"   - Animes inseridos: {inserted_count}")
        write_log(log_file, "🎉 Atualização dos animes antecipados concluída com sucesso!")

if __name__ == '__main__':
    try:
        update_anticipated_animes_data()
    except Exception as e:
        print_log(f"❌ ERRO: {str(e)}")
        print_log("📋 Verifique o arquivo 'anticipated_debug.log' para mais detalhes")
        import traceback
        print_log("🔍 Traceback completo:")
        traceback.print_exc()
        input("Pressione Enter para sair...")  # Manter console aberto