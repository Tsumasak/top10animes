#!/usr/bin/env python3
"""
Verificar dados exportados
"""

import json
import os

def check_exported_data():
    print("📊 VERIFICANDO DADOS EXPORTADOS")
    print("=" * 40)
    
    # Ler dados exportados
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    episodes_file = os.path.join(base_dir, 'frontend', 'public', 'episodes_data.json')
    
    if not os.path.exists(episodes_file):
        print("❌ Arquivo episodes_data.json não encontrado")
        return
    
    with open(episodes_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Filtrar episódios manuais
    manual_eps = [ep for ep in data if ep.get('is_manual') == 1]
    auto_eps = [ep for ep in data if ep.get('is_manual') != 1]
    
    print(f"📈 Total de episódios: {len(data)}")
    print(f"🤖 Episódios automáticos: {len(auto_eps)}")
    print(f"✋ Episódios manuais: {len(manual_eps)}")
    
    if manual_eps:
        print(f"\n🔍 EPISÓDIOS MANUAIS EXPORTADOS:")
        for ep in manual_eps[:3]:
            print(f"   🎬 {ep['anime_title']}")
            print(f"   📺 {ep['title']}")
            print(f"   ⭐ Rating: {ep['rating']}")
            print(f"   🔗 URL: {ep['episode_url']}")
            print(f"   🖼️ Imagem: {ep['anime_image_url']}")
            print()
        
        # Verificar se está seguindo padrão correto
        manual_ep = manual_eps[0]
        checks = {
            "Título formatado (EP X • Nome)": "EP " in manual_ep['title'] and " • " in manual_ep['title'],
            "URL com offset": "?offset=" in manual_ep['episode_url'],
            "Imagem large": "large" in manual_ep['anime_image_url'] or manual_ep['anime_image_url'].endswith('l.jpg'),
            "Sem indicador visual": "🔧" not in manual_ep['title']
        }
        
        print("✅ VALIDAÇÕES:")
        for check, result in checks.items():
            status = "✅" if result else "❌"
            print(f"   {status} {check}")
    
    else:
        print("📦 Nenhum episódio manual encontrado nos dados exportados")

if __name__ == '__main__':
    check_exported_data()