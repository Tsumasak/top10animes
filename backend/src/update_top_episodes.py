import sqlite3
import time
import math
import os
from datetime import datetime, timedelta, date
from jikan_api import get_top_airing_anime, get_anime_episodes, get_custom_seasons_anime
from database_setup import setup_database

def print_log(message):
    """Print message to console with timestamp"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")

def calculate_week_periods():
    """
    Calculate the date ranges for different week periods based on current date.
    Returns dictionary with period options and their date ranges.
    """
    today = datetime.now().date()
    
    # Find Monday of current week (today is Sunday=6, Monday=0)
    days_since_monday = today.weekday()  # Monday = 0, Sunday = 6
    current_monday = today - timedelta(days=days_since_monday)
    
    # Week periods calculation
    periods = {}
    
    # 1. Semana Atual: From Monday of current week until today
    periods['semana_atual'] = {
        'name': 'Semana Atual',
        'start_date': current_monday,
        'end_date': today,
        'description': f"De {current_monday.strftime('%d/%m/%Y')} até {today.strftime('%d/%m/%Y')}"
    }
    
    # 2. Semana passada: Last complete week (Sunday to Monday)
    last_sunday = current_monday - timedelta(days=1)
    last_monday = last_sunday - timedelta(days=6)
    periods['semana_passada'] = {
        'name': 'Semana passada',
        'start_date': last_monday,
        'end_date': last_sunday,
        'description': f"De {last_monday.strftime('%d/%m/%Y')} até {last_sunday.strftime('%d/%m/%Y')}"
    }
    
    # 3. Semana anterior: Week before last week
    prev_sunday = last_monday - timedelta(days=1)
    prev_monday = prev_sunday - timedelta(days=6)
    periods['semana_anterior'] = {
        'name': 'Semana anterior',
        'start_date': prev_monday,
        'end_date': prev_sunday,
        'description': f"De {prev_monday.strftime('%d/%m/%Y')} até {prev_sunday.strftime('%d/%m/%Y')}"
    }
    
    # 4. 3 semanas atrás: Three weeks ago
    three_weeks_sunday = prev_monday - timedelta(days=1)
    three_weeks_monday = three_weeks_sunday - timedelta(days=6)
    periods['tres_semanas'] = {
        'name': '3 semanas atrás',
        'start_date': three_weeks_monday,
        'end_date': three_weeks_sunday,
        'description': f"De {three_weeks_monday.strftime('%d/%m/%Y')} até {three_weeks_sunday.strftime('%d/%m/%Y')}"
    }
    
    return periods

def show_period_menu():
    """
    Display interactive menu for period selection and return selected period.
    Returns tuple: (start_date, end_date) or None for custom period
    """
    periods = calculate_week_periods()
    
    print_log("📅 Selecione o período para coleta de episódios:")
    print()
    
    # Show predefined options
    options = ['semana_atual', 'semana_passada', 'semana_anterior', 'tres_semanas']
    for i, period_key in enumerate(options, 1):
        period = periods[period_key]
        print(f"  {i}. {period['name']}")
        print(f"     {period['description']}")
        print()
    
    print(f"  5. Período Personalizado")
    print(f"     Definir data inicial e final manualmente")
    print()
    
    # Get user choice
    while True:
        try:
            choice = input("Digite sua escolha (1-5): ").strip()
            
            if choice in ['1', '2', '3', '4']:
                period_key = options[int(choice) - 1]
                selected_period = periods[period_key]
                print_log(f"✅ Selecionado: {selected_period['name']} - {selected_period['description']}")
                return selected_period['start_date'], selected_period['end_date']
            
            elif choice == '5':
                return get_custom_period()
            
            else:
                print("❌ Opção inválida. Digite um número de 1 a 5.")
                
        except (ValueError, KeyboardInterrupt):
            print("❌ Entrada inválida. Digite um número de 1 a 5.")

def get_custom_period():
    """
    Get custom period from user input with validation.
    Returns tuple: (start_date, end_date)
    """
    print_log("📝 Definindo período personalizado...")
    print("Formato de data: DD/MM/YYYY (ex: 13/10/2025)")
    print()
    
    while True:
        try:
            start_str = input("Data inicial: ").strip()
            start_date = datetime.strptime(start_str, "%d/%m/%Y").date()
            break
        except ValueError:
            print("❌ Formato inválido. Use DD/MM/YYYY (ex: 13/10/2025)")
    
    while True:
        try:
            end_str = input("Data final: ").strip()
            end_date = datetime.strptime(end_str, "%d/%m/%Y").date()
            
            if end_date < start_date:
                print("❌ Data final deve ser posterior à data inicial.")
                continue
            break
        except ValueError:
            print("❌ Formato inválido. Use DD/MM/YYYY (ex: 13/10/2025)")
    
    print_log(f"✅ Período personalizado: {start_date.strftime('%d/%m/%Y')} até {end_date.strftime('%d/%m/%Y')}")
    return start_date, end_date

def update_top_episodes_data(seasons_to_fetch=None, days_threshold=45, interactive=True, custom_period=None):
    """
    Update top episodes data with configurable parameters.
    
    Args:
        seasons_to_fetch: List of (year, season) tuples to fetch from. 
                         If None, uses current + previous seasons.
                         Example: [(2025, 'summer'), (2025, 'fall')]
        days_threshold: Maximum days since last episode aired (default: 45)
        interactive: If True, show menu for period selection
        custom_period: Tuple (start_date, end_date) for custom period filtering
    """
    print_log("🚀 Iniciando atualização dos top episódios...")
    
    setup_database() # Ensure tables exist
    print_log("✅ Database configurado")
    
    # Period selection logic
    if interactive and not custom_period and not seasons_to_fetch:
        print()
        custom_period = show_period_menu()
        print()
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(os.path.dirname(script_dir), 'top10animes.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    print_log(f"📁 Conectado ao banco: {db_path}")

    if custom_period:
        start_date, end_date = custom_period
        days_diff = (end_date - start_date).days + 1
        print_log(f"📊 Configuração: período personalizado ({days_diff} dias)")
        print_log(f"📅 Período: {start_date.strftime('%d/%m/%Y')} até {end_date.strftime('%d/%m/%Y')}")
    else:
        print_log(f"📊 Configuração: threshold de {days_threshold} dias")
        
    if seasons_to_fetch:
        seasons_str = [f"{s[1]} {s[0]}" for s in seasons_to_fetch]
        print_log(f"📅 Buscando temporadas específicas: {seasons_str}")
        episodes_data = get_custom_seasons_anime(seasons_to_fetch)
    else:
        print_log("📅 Buscando animes atuais em exibição...")
        episodes_data = get_top_airing_anime()
    c.execute("DELETE FROM episodes")
    
    for item in episodes_data['data']:
        anime_id = item.get('mal_id')
        anime_type = item.get('type')
        status = item.get('status')
        
        # Filter by type first to determine status rules
        if anime_type not in ['TV', 'ONA']:
            continue # Skip this anime
        
        # Status filter: TV must be Currently Airing, ONA can be Currently Airing or Not yet aired
        if anime_type == 'TV' and status != 'Currently Airing':
            continue # Skip this anime
        elif anime_type == 'ONA' and status not in ['Currently Airing', 'Not yet aired']:
            continue # Skip this anime

        # Filter out problematic anime IDs (known to have stale "Currently Airing" status or very old episodes)
        problematic_ids = [
            9874,   # Touhou Niji Sousaku Doujin Anime: Musou Kakyou (last episode 2021)
            36686,  # Hifuu Katsudou Kiroku: The Sealed Esoteric History (old episodes)
            44042,  # Holo no Graffiti (old episodes, confirmed problematic)
            50250,  # Chiikawa (last episode Sept 2022)
            51289,  # Zhe Tian (last episode July 2024)
            51836,  # Douluo Dalu II: Jueshi Tangmen (last episode June 2023)
            # Add more problematic anime IDs as discovered
        ]
        if anime_id in problematic_ids:
            continue # Skip problematic anime

        # Requirement 3: Filter by members > 15000
        members = item.get('members', 0)
        if members < 15000:
            continue # Skip this anime

        # Requirement 2: Get English title, fallback to default
        anime_title = item.get('title_english') # Try English title first
        if not anime_title: # Fallback to default title if English not found
            anime_title = item.get('title')

        anime_image_url = item['images']['jpg']['large_image_url']
        
        episode_number = 0
        episode_rating = 0.0
        episode_url = ''
        episode_name = '' # New variable for episode name

        total_episodes_fallback = item.get('episodes') or 0 # Get total episodes as fallback

        try:
            anime_episodes_data = get_anime_episodes(anime_id)
            if anime_episodes_data['data']:
                latest_episode = anime_episodes_data['data'][-1]
                episode_number = latest_episode.get('mal_id') or 0
                episode_rating = latest_episode.get('score') or 0.0
                episode_name = latest_episode.get('title', '')
                
                # Check if latest episode is recent (within last 45 days)
                episode_aired = latest_episode.get('aired')
                if episode_aired:
                    try:
                        aired_date = datetime.fromisoformat(episode_aired.replace('Z', '+00:00'))
                        aired_date_only = aired_date.date()
                        
                        # Use custom period if specified, otherwise use days threshold
                        if custom_period:
                            start_date, end_date = custom_period
                            today = datetime.now().date()
                            
                            # Check if episode is outside period
                            if aired_date_only < start_date or aired_date_only > end_date:
                                # Special handling for future dates that might be incorrect in API
                                if aired_date_only > today:
                                    # Calculate how many days in the future
                                    days_in_future = (aired_date_only - today).days
                                    
                                    # If it's within 7 days in the future and the period includes recent dates,
                                    # consider it might be a data error and include it
                                    if days_in_future <= 7 and end_date >= today - timedelta(days=3):
                                        print(f"⚠️  {anime_title}: Episode dated {aired_date_only.strftime('%d/%m/%Y')} (future), but including due to likely API error (only {days_in_future} days ahead)")
                                        # Continue processing this episode - don't skip it
                                    else:
                                        # Try previous episode for dates further in future
                                        if len(anime_episodes_data['data']) > 1:
                                            print(f"Latest episode is in future ({aired_date_only.strftime('%d/%m/%Y')}), checking previous episode...")
                                            
                                            # Get previous episode (second to last)
                                            previous_episode = anime_episodes_data['data'][-2]
                                            prev_episode_aired = previous_episode.get('aired')
                                            
                                            if prev_episode_aired:
                                                try:
                                                    prev_aired_date = datetime.fromisoformat(prev_episode_aired.replace('Z', '+00:00'))
                                                    prev_aired_date_only = prev_aired_date.date()
                                                    
                                                    # Check if previous episode is within period
                                                    if prev_aired_date_only >= start_date and prev_aired_date_only <= end_date:
                                                        print(f"Using previous episode: {anime_title} EP {previous_episode.get('mal_id', 0)} aired on {prev_aired_date_only.strftime('%d/%m/%Y')}")
                                                        # Replace current episode data with previous episode
                                                        latest_episode = previous_episode
                                                        episode_number = previous_episode.get('mal_id') or 0
                                                        episode_rating = previous_episode.get('score') or 0.0
                                                        episode_name = previous_episode.get('title', '')
                                                        aired_date_only = prev_aired_date_only
                                                    else:
                                                        print(f"Skipping {anime_title}: Previous episode aired on {prev_aired_date_only.strftime('%d/%m/%Y')} (also outside period)")
                                                        continue
                                                except Exception as prev_date_error:
                                                    print(f"Skipping {anime_title}: Could not parse previous episode date - Error: {str(prev_date_error)}, Raw date: {prev_episode_aired}")
                                                    continue
                                            else:
                                                print(f"Skipping {anime_title}: Previous episode has no air date")
                                                continue
                                        else:
                                            print(f"Skipping {anime_title}: Episode aired on {aired_date_only.strftime('%d/%m/%Y')} (future date, no previous episodes)")
                                            continue
                                else:
                                    print(f"Skipping {anime_title}: Episode aired on {aired_date_only.strftime('%d/%m/%Y')} (outside period)")
                                    continue
                        else:
                            days_since_aired = (datetime.now().replace(tzinfo=aired_date.tzinfo) - aired_date).days
                            # Skip anime if latest episode is older than threshold
                            if days_since_aired > days_threshold:
                                print(f"Skipping {anime_title}: Last episode aired {days_since_aired} days ago (threshold: {days_threshold})")
                                continue
                    except Exception as date_error:
                        # If we can't parse the date, skip this anime to be safe
                        print(f"Skipping {anime_title}: Could not parse episode date - Error: {str(date_error)}, Raw date: {episode_aired}")
                        continue
                else:
                    # No air date - try to infer recency from previous episodes
                    print(f"Episode {episode_number} of {anime_title} has no date - checking previous episodes...")
                    
                    # Get all episodes to analyze pattern
                    all_episodes = anime_episodes_data['data']
                    episodes_with_dates = []
                    
                    for ep in all_episodes:
                        ep_aired = ep.get('aired')
                        if ep_aired:
                            try:
                                ep_date = datetime.fromisoformat(ep_aired.replace('Z', '+00:00'))
                                episodes_with_dates.append((ep.get('mal_id'), ep_date))
                            except:
                                continue
                    
                    # If we have recent episodes with dates, infer this one is also recent
                    if episodes_with_dates:
                        # Sort by episode number to get chronological order
                        episodes_with_dates.sort(key=lambda x: x[0])
                        latest_dated_episode = episodes_with_dates[-1]
                        latest_date = latest_dated_episode[1]
                        
                        # Check if the latest dated episode is within period
                        latest_date_only = latest_date.date()
                        
                        if custom_period:
                            start_date, end_date = custom_period
                            if latest_date_only >= start_date and latest_date_only <= end_date:
                                print(f"Inferred {anime_title} EP {episode_number} is recent (latest dated episode was {latest_date_only.strftime('%d/%m/%Y')})")
                                # Continue processing this anime - it's within period
                            else:
                                print(f"Skipping {anime_title}: Latest dated episode was {latest_date_only.strftime('%d/%m/%Y')} (outside period)")
                                continue
                        else:
                            days_since_latest = (datetime.now().replace(tzinfo=latest_date.tzinfo) - latest_date).days
                            if days_since_latest <= days_threshold:
                                print(f"Inferred {anime_title} EP {episode_number} is recent (latest dated episode was {days_since_latest} days ago)")
                                # Continue processing this anime - it's likely recent
                            else:
                                print(f"Skipping {anime_title}: Latest dated episode was {days_since_latest} days ago (threshold: {days_threshold})")
                                continue
                    else:
                        # No episodes with dates found, skip to be safe
                        print(f"Skipping {anime_title}: No episodes with dates found for inference")
                        continue
            else:
                episode_number = total_episodes_fallback # Use total episodes if specific data is empty
            
            time.sleep(0.5)
        except Exception as e:
            # Silently ignore errors for single anime to not stop the whole process
            episode_number = total_episodes_fallback # Use total episodes on error
            pass

        # Requirement 1: Format episode name
        formatted_episode_title = f"EP {episode_number} • {episode_name}" if episode_name else f"EP {episode_number}"

        # Construct the MAL episode URL
        if episode_number > 0:
            url_anime_title_for_mal = anime_title.replace(' ', '_') # Use the (English) anime title
            offset = math.floor((episode_number - 1) / 100) * 100
            episode_url = f"https://myanimelist.net/anime/{anime_id}/{url_anime_title_for_mal}/episode?offset={offset}"

        # Update INSERT statement to include anime_type and formatted_episode_title
        c.execute("INSERT INTO episodes (id, anime_id, title, episode_number, rating, anime_title, anime_image_url, episode_url, anime_type) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                  (f"{anime_id}-{episode_number}", anime_id, formatted_episode_title, episode_number, episode_rating, anime_title, anime_image_url, episode_url, anime_type))

    conn.commit()
    conn.close()
    
    print_log(f"📊 Estatísticas finais:")
    print_log(f"   - Episódios processados: {len([ep for ep in episodes_data['data'] if ep.get('rating')])}")  
    print_log("🎉 Atualização dos top episódios concluída com sucesso!")

if __name__ == '__main__':
    try:
        # Exemplo: Para coletar de Summer 2025 e Fall 2025 com episódios dos últimos 60 dias
        # seasons_to_collect = [(2025, 'summer'), (2025, 'fall')]
        # update_top_episodes_data(seasons_to_collect, days_threshold=60)
        
        # Para usar comportamento padrão (automático)
        update_top_episodes_data()
    except Exception as e:
        print_log(f"❌ ERRO: {str(e)}")
        import traceback
        print_log("🔍 Traceback completo:")
        traceback.print_exc()
        input("Pressione Enter para sair...")  # Manter console aberto
