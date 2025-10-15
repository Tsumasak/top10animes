import sqlite3
import os

def setup_database():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(os.path.dirname(script_dir), 'top10animes.db')
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS episodes (
            id TEXT PRIMARY KEY,
            anime_id INTEGER,
            title TEXT,
            episode_number INTEGER,
            rating REAL,
            anime_title TEXT,
            anime_image_url TEXT,
            episode_url TEXT,
            anime_type TEXT
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS anticipated_animes (
            id INTEGER PRIMARY KEY,
            title TEXT,
            image_url TEXT,
            members INTEGER,
            season TEXT,
            year INTEGER,
            mal_url TEXT,
            demographics TEXT,
            genres TEXT,
            themes TEXT
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS manual_episodes (
            id TEXT PRIMARY KEY,
            anime_id INTEGER,
            title TEXT,
            episode_number INTEGER,
            rating REAL,
            anime_title TEXT,
            anime_image_url TEXT,
            episode_url TEXT,
            anime_type TEXT,
            date_added TEXT,
            air_date TEXT,
            is_manual INTEGER DEFAULT 1
        )
    ''')
    
    # Add themes column if it doesn't exist (for existing databases)
    try:
        c.execute('ALTER TABLE anticipated_animes ADD COLUMN themes TEXT DEFAULT "[]"')
        print("Added themes column to anticipated_animes table")
    except sqlite3.OperationalError:
        # Column already exists
        pass
    
    # Add air_date column to manual_episodes if it doesn't exist (for existing databases)
    try:
        c.execute('ALTER TABLE manual_episodes ADD COLUMN air_date TEXT')
        print("Added air_date column to manual_episodes table")
    except sqlite3.OperationalError:
        # Column already exists or table doesn't exist yet
        pass

    conn.commit()
    conn.close()

if __name__ == '__main__':
    setup_database()
