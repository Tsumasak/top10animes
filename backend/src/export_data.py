import sqlite3
import json
import os

def export_data():
    # Get the absolute path to the directory of the current script (backend/src)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    db_path = os.path.join(os.path.dirname(script_dir), 'top10animes.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    # Define the output paths relative to the project root
    project_root = os.path.dirname(os.path.dirname(script_dir))
    episodes_output_path = os.path.join(project_root, 'frontend', 'public', 'episodes_data.json')
    anticipated_output_path = os.path.join(project_root, 'frontend', 'public', 'anticipated_animes_data.json')

    # Export episodes - Filter out episodes with rating 0 (not yet released)
    # Include both regular episodes and manual episodes
    c.execute("""
        SELECT anime_id, title, episode_number, rating, anime_title, anime_image_url, episode_url, anime_type, 0 as is_manual
        FROM episodes 
        WHERE rating > 0
        
        UNION ALL
        
        SELECT anime_id, title, episode_number, rating, anime_title, anime_image_url, episode_url, anime_type, 1 as is_manual
        FROM manual_episodes
        WHERE rating > 0
        
        ORDER BY rating DESC
    """)
    episodes = [dict(row) for row in c.fetchall()]
    with open(episodes_output_path, 'w') as f:
        json.dump(episodes, f, indent=2)

    # Export anticipated animes
    c.execute("SELECT id, title, image_url, members, season, year, mal_url, demographics, genres, themes FROM anticipated_animes ORDER BY members DESC")
    anticipated_animes_raw = [dict(row) for row in c.fetchall()]
    
    # Parse JSON fields for demographics, genres, and themes
    anticipated_animes = []
    for anime in anticipated_animes_raw:
        anime_dict = dict(anime)
        # Parse demographics, genres, and themes from JSON strings
        try:
            anime_dict['demographics'] = json.loads(anime['demographics']) if anime['demographics'] else []
            anime_dict['genres'] = json.loads(anime['genres']) if anime['genres'] else []
            anime_dict['themes'] = json.loads(anime['themes']) if anime['themes'] else []
        except (json.JSONDecodeError, TypeError):
            anime_dict['demographics'] = []
            anime_dict['genres'] = []
            anime_dict['themes'] = []
        anticipated_animes.append(anime_dict)
    
    with open(anticipated_output_path, 'w') as f:
        json.dump(anticipated_animes, f, indent=4)

    conn.close()

if __name__ == '__main__':
    export_data()
