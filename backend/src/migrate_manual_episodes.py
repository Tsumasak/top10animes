#!/usr/bin/env python3
"""
Migrar episódios manuais existentes para novo padrão
"""

import sqlite3
import os
import math
from manual_episodes import ManualEpisodeManager

def migrate_existing_episodes():
    print("🔄 MIGRANDO EPISÓDIOS MANUAIS EXISTENTES")
    print("=" * 50)
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(os.path.dirname(script_dir), 'top10animes.db')
    
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # Buscar episódios manuais existentes
    c.execute('SELECT id, anime_id, title, episode_number, anime_title FROM manual_episodes')
    episodes = c.fetchall()
    
    if not episodes:
        print("📦 Nenhum episódio manual encontrado para migrar")
        return
    
    manager = ManualEpisodeManager()
    
    for episode_id, anime_id, old_title, episode_number, anime_title in episodes:
        print(f"\n📝 Migrando: {anime_title} - {old_title}")
        
        # Buscar informações atualizadas do anime
        anime_info = manager.get_anime_info(anime_id)
        if not anime_info:
            print(f"   ❌ Não foi possível buscar info do anime {anime_id}")
            continue
        
        # Extrair nome do episódio do título antigo
        if " • " in old_title:
            episode_name = old_title.split(" • ", 1)[1]
        else:
            episode_name = old_title.replace(f"EP {episode_number}", "").strip()
            if episode_name.startswith("• "):
                episode_name = episode_name[2:]
        
        # Aplicar novo padrão
        anime_display_title = anime_info.get('title_english') or anime_info['title']
        formatted_episode_title = f"EP {episode_number} • {episode_name}"
        
        # Construir URL correta
        url_anime_title_for_mal = anime_display_title.replace(' ', '_')
        offset = math.floor((episode_number - 1) / 100) * 100
        episode_url = f"https://myanimelist.net/anime/{anime_id}/{url_anime_title_for_mal}/episode?offset={offset}"
        
        # Atualizar no banco
        c.execute('''
            UPDATE manual_episodes 
            SET title = ?, anime_title = ?, anime_image_url = ?, episode_url = ?
            WHERE id = ?
        ''', (
            formatted_episode_title,
            anime_display_title, 
            anime_info['image_url'],
            episode_url,
            episode_id
        ))
        
        print(f"   ✅ Título: {old_title} → {formatted_episode_title}")
        print(f"   ✅ Anime: {anime_title} → {anime_display_title}")
        print(f"   ✅ URL: {episode_url}")
        print(f"   ✅ Imagem: large_image_url aplicada")
    
    conn.commit()
    conn.close()
    
    print(f"\n🎉 {len(episodes)} episódio(s) migrado(s) com sucesso!")

if __name__ == '__main__':
    migrate_existing_episodes()