import requests
import datetime
import time # Import time for sleep

# Helper to fetch multiple pages from Jikan API
def _fetch_paginated_anime(base_url: str, initial_params: dict, max_items: int = 50):
    all_anime = []
    page = 1
    has_next_page = True

    while has_next_page and len(all_anime) < max_items:
        params = {**initial_params, "page": page}
        
        # Retry logic for rate limiting
        max_retries = 3
        retry_count = 0
        while retry_count < max_retries:
            try:
                response = requests.get(base_url, params=params)
                response.raise_for_status()
                break
            except requests.exceptions.HTTPError as e:
                if response.status_code == 429:  # Rate limit
                    retry_count += 1
                    wait_time = 2 ** retry_count  # Exponential backoff: 2, 4, 8 seconds
                    print(f"Rate limited. Waiting {wait_time} seconds before retry {retry_count}/{max_retries}...")
                    time.sleep(wait_time)
                    if retry_count >= max_retries:
                        raise e
                else:
                    raise e
        
        data = response.json()
        all_anime.extend(data['data'])
        has_next_page = data['pagination']['has_next_page']
        page += 1
        time.sleep(0.2)  # Be respectful to the API

    return {"data": all_anime, "pagination": data['pagination']} # Return collected data and last pagination info

def get_top_airing_anime():
    """Fetches anime from current season (and previous season as fallback) from Jikan API."""
    from datetime import datetime
    
    all_anime = []
    
    # 1. Get current season anime (/seasons/now - matches MAL season page)
    print("Fetching current season anime...")
    base_url = "https://api.jikan.moe/v4/seasons/now"
    params = {"limit": 25}
    current_season_data = _fetch_paginated_anime(base_url, params, max_items=100)
    all_anime.extend(current_season_data['data'])
    
    # 2. Get previous season as fallback (for season transition periods)
    print("Fetching previous season anime as fallback...")
    current_date = datetime.now()
    month = current_date.month
    
    # Determine current and previous season
    if month in [12, 1, 2]:
        current_season = "winter"
        prev_season, prev_year = "fall", current_date.year - (1 if month != 12 else 0)
    elif month in [3, 4, 5]:
        current_season = "spring"
        prev_season, prev_year = "winter", current_date.year
    elif month in [6, 7, 8]:
        current_season = "summer"
        prev_season, prev_year = "spring", current_date.year
    else:  # [9, 10, 11]
        current_season = "fall"
        prev_season, prev_year = "summer", current_date.year
    
    try:
        prev_season_url = f"https://api.jikan.moe/v4/seasons/{prev_year}/{prev_season}"
        prev_season_data = _fetch_paginated_anime(prev_season_url, params, max_items=50)
        all_anime.extend(prev_season_data['data'])
        print(f"Added {len(prev_season_data['data'])} anime from {prev_season} {prev_year}")
    except Exception as e:
        print(f"Warning: Could not fetch previous season data: {e}")
    
    # Remove duplicates by anime_id and filter by status
    seen_ids = set()
    unique_anime = []
    filtered_count = 0
    
    for anime in all_anime:
        anime_id = anime.get('mal_id')
        status = anime.get('status', '')
        
        # Skip duplicates
        if anime_id in seen_ids:
            continue
            
        seen_ids.add(anime_id)
        
        # Filter out "Finished Airing" anime to optimize processing
        if status == 'Finished Airing':
            filtered_count += 1
            continue
            
        # Keep only active anime that might have new episodes
        if status in ['Currently Airing', 'Not yet aired']:
            unique_anime.append(anime)
    
    print(f"Total unique anime after combining seasons: {len(all_anime)} -> {len(unique_anime)} active")
    print(f"Filtered out {filtered_count} 'Finished Airing' anime for optimization")
    return {"data": unique_anime, "pagination": current_season_data.get('pagination', {})}

def get_custom_seasons_anime(seasons_list):
    """
    Fetches anime from specified seasons.
    
    Args:
        seasons_list: List of (year, season) tuples
                      Example: [(2025, 'summer'), (2025, 'fall')]
    """
    all_anime = []
    
    for year, season in seasons_list:
        print(f"Fetching anime from {season} {year}...")
        try:
            base_url = f"https://api.jikan.moe/v4/seasons/{year}/{season}"
            params = {"limit": 25}
            season_data = _fetch_paginated_anime(base_url, params, max_items=100)
            all_anime.extend(season_data['data'])
            print(f"Added {len(season_data['data'])} anime from {season} {year}")
        except Exception as e:
            print(f"Warning: Could not fetch {season} {year} data: {e}")
    
    # Remove duplicates by anime_id and filter by status
    seen_ids = set()
    unique_anime = []
    filtered_count = 0
    
    for anime in all_anime:
        anime_id = anime.get('mal_id')
        status = anime.get('status', '')
        
        # Skip duplicates
        if anime_id in seen_ids:
            continue
            
        seen_ids.add(anime_id)
        
        # Filter out "Finished Airing" anime to optimize processing
        if status == 'Finished Airing':
            filtered_count += 1
            continue
            
        # Keep only active anime that might have new episodes
        if status in ['Currently Airing', 'Not yet aired']:
            unique_anime.append(anime)
    
    print(f"Total unique anime from custom seasons: {len(all_anime)} -> {len(unique_anime)} active")
    print(f"Filtered out {filtered_count} 'Finished Airing' anime for optimization")
    return {"data": unique_anime, "pagination": {}}

def get_anime_episodes(anime_id):
    """
    Fetches episode details for a given anime ID from the Jikan API,
    handling pagination to retrieve the last page of episodes.
    """
    base_url = f"https://api.jikan.moe/v4/anime/{anime_id}/episodes"
    
    # First, get the first page to determine total pages
    response = requests.get(base_url)
    response.raise_for_status()
    first_page_data = response.json()

    last_visible_page = first_page_data['pagination']['last_visible_page']

    if last_visible_page > 1:
        # If there's more than one page, fetch the last page
        last_page_url = f"{base_url}?page={last_visible_page}"
        response = requests.get(last_page_url)
        response.raise_for_status()
        return response.json()
    else:
        # If only one page, return the data from the first page
        return first_page_data

def get_season_anime(year: int, season: str):
    """Fetches anime for a specific season and year from the Jikan API."""
    base_url = f"https://api.jikan.moe/v4/seasons/{year}/{season.lower()}"
    params = {
        "limit": 25 # Use a safe limit per page
    }
    return _fetch_paginated_anime(base_url, params, max_items=50) # Fetch up to 50 items

def get_upcoming_anime():
    """Fetches all upcoming anime from the Jikan API."""
    base_url = "https://api.jikan.moe/v4/seasons/upcoming"
    params = {
        "limit": 25 # Use a safe limit per page
    }
    return _fetch_paginated_anime(base_url, params, max_items=100) # Fetch more for 'Later'

def get_anime_full_details(anime_id: int):
    """Fetches complete details for a specific anime including demographics and genres."""
    base_url = f"https://api.jikan.moe/v4/anime/{anime_id}"
    
    # Retry logic for rate limiting
    max_retries = 3
    retry_count = 0
    while retry_count < max_retries:
        try:
            response = requests.get(base_url)
            response.raise_for_status()
            break
        except requests.exceptions.HTTPError as e:
            if response.status_code == 429:  # Rate limit
                retry_count += 1
                wait_time = 2 ** retry_count  # Exponential backoff: 2, 4, 8 seconds
                print(f"Rate limited on anime {anime_id}. Waiting {wait_time} seconds before retry {retry_count}/{max_retries}...")
                time.sleep(wait_time)
                if retry_count >= max_retries:
                    raise e
            else:
                raise e
    
    time.sleep(0.3)  # Be respectful to the API
    return response.json()
