#!/usr/bin/env python3
"""
Teste da correção do parser de rating
"""

from manual_episodes import ManualEpisodeManager

def test_corrected_parser():
    print("🧪 TESTANDO PARSER CORRIGIDO")
    print("=" * 40)
    
    manager = ManualEpisodeManager()
    
    # Teste com o formato problemático
    problematic_input = """5Loved it!
72.7%
197
4Liked it!
21.0%
57
3It was OK
4.8%
13
2Disliked it
0.4%
1
1Hated it
1.1%
3"""
    
    print("📝 Testando formato problemático:")
    print("Input:")
    print(problematic_input)
    print("\nProcessando...")
    
    result = manager.parse_rating_data(problematic_input)
    print(f"✅ Resultado: {result}")
    
    if result > 0:
        print("🎉 SUCESSO! O parser agora funciona com formato separado!")
    else:
        print("❌ Ainda há problemas...")
    
    # Teste com formato normal também
    normal_input = """5Loved it! 72.7% 197
4Liked it! 21.0% 57
3It was OK 4.8% 13
2Disliked it 0.4% 1
1Hated it 1.1% 3"""
    
    print("\n📝 Testando formato normal:")
    result2 = manager.parse_rating_data(normal_input)
    print(f"✅ Resultado: {result2}")
    
    if result == result2:
        print("🎉 PERFEITO! Ambos os formatos geram o mesmo resultado!")
    else:
        print(f"⚠️ Resultados diferentes: {result} vs {result2}")

if __name__ == '__main__':
    test_corrected_parser()