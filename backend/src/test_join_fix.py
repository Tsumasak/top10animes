#!/usr/bin/env python3
"""
Teste da correção do join
"""

from manual_episodes import ManualEpisodeManager

def test_input_processing():
    print("🧪 TESTANDO PROCESSAMENTO DE INPUT")
    print("=" * 40)
    
    # Simular o que acontece no sistema interativo
    rating_lines = [
        '5Loved it!',
        '72.7%', 
        '197',
        '4Liked it!',
        '21.0%',
        '57',
        '3It was OK',
        '4.8%',
        '13',
        '2Disliked it',
        '0.4%',
        '1',
        '1Hated it',
        '1.1%',
        '3'
    ]
    
    # Método antigo (INCORRETO)
    old_method = ' '.join(rating_lines)
    print("❌ Método antigo (space join):")
    print(f"'{old_method}'")
    
    manager = ManualEpisodeManager()
    old_result = manager.parse_rating_data(old_method)
    print(f"Resultado: {old_result}")
    
    # Método novo (CORRETO)
    new_method = '\n'.join(rating_lines)
    print("\n✅ Método novo (newline join):")
    print(f"'{new_method}'")
    
    new_result = manager.parse_rating_data(new_method)
    print(f"Resultado: {new_result}")
    
    print(f"\n🎯 COMPARAÇÃO:")
    print(f"Antigo: {old_result}")
    print(f"Novo: {new_result}")
    print(f"Esperado: 4.64")

if __name__ == '__main__':
    test_input_processing()