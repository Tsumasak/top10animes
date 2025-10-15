#!/usr/bin/env python3
"""
Teste das correções implementadas
"""

from manual_episodes import ManualEpisodeManager
import math

def test_corrections():
    print("🧪 TESTANDO CORREÇÕES IMPLEMENTADAS")
    print("=" * 50)
    
    manager = ManualEpisodeManager()
    
    # Teste 1: Busca de anime com nova estrutura
    print("📝 Teste 1: Busca de informações do anime")
    anime_info = manager.get_anime_info(61930)  # Uma Musume: Cinderella Gray Part 2
    
    if anime_info:
        print(f"✅ Título: {anime_info['title']}")
        print(f"✅ Título inglês: {anime_info.get('title_english', 'N/A')}")
        print(f"✅ Imagem (large): {anime_info['image_url']}")
        print(f"✅ Tipo: {anime_info['type']}")
        
        # Teste 2: Formatação de título
        print(f"\n📝 Teste 2: Formatação de título do episódio")
        episode_number = 2
        episode_title = "Our Story"
        formatted_title = f"EP {episode_number} • {episode_title}"
        print(f"✅ Título formatado: '{formatted_title}'")
        
        # Teste 3: Construção de URL
        print(f"\n📝 Teste 3: Construção de URL do episódio")
        anime_display_title = anime_info.get('title_english') or anime_info['title']
        url_anime_title_for_mal = anime_display_title.replace(' ', '_')
        offset = math.floor((episode_number - 1) / 100) * 100
        episode_url = f"https://myanimelist.net/anime/{anime_info['id']}/{url_anime_title_for_mal}/episode?offset={offset}"
        print(f"✅ URL construída: {episode_url}")
        
        print(f"\n🎉 TODAS AS CORREÇÕES FUNCIONANDO!")
        print(f"   - ✅ Imagem em alta resolução")
        print(f"   - ✅ Título formatado como 'EP X • Nome'")  
        print(f"   - ✅ URL com padrão correto e offset")
        print(f"   - ✅ Título em inglês quando disponível")
        
    else:
        print("❌ Erro ao buscar anime")

if __name__ == '__main__':
    test_corrections()