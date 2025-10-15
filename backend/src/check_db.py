#!/usr/bin/env python3
"""
Verificar dados no banco
"""

import sqlite3
import os

def check_database():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(os.path.dirname(script_dir), 'top10animes.db')
    
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # Verificar episódios manuais
    c.execute('SELECT COUNT(*) FROM manual_episodes')
    manual_count = c.fetchone()[0]
    print(f"📊 Episódios manuais no banco: {manual_count}")
    
    if manual_count > 0:
        c.execute('SELECT anime_title, title, rating, episode_url FROM manual_episodes LIMIT 3')
        episodes = c.fetchall()
        print("\n📋 Exemplos de episódios manuais:")
        for ep in episodes:
            print(f"   🎬 {ep[0]}")
            print(f"   📺 {ep[1]}")
            print(f"   ⭐ Rating: {ep[2]}")
            print(f"   🔗 URL: {ep[3]}")
            print()
    
    # Verificar episódios automáticos também
    c.execute('SELECT COUNT(*) FROM episodes WHERE rating > 0')
    auto_count = c.fetchone()[0]
    print(f"📊 Episódios automáticos no banco: {auto_count}")
    
    conn.close()

if __name__ == '__main__':
    check_database()