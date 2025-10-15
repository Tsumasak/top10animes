#!/usr/bin/env python3
"""
Debug detalhado do cálculo de rating
"""

from manual_episodes import ManualEpisodeManager

def debug_rating_calculation():
    print("🔍 DEBUG DETALHADO DO CÁLCULO")
    print("=" * 40)
    
    # Dados exatos do usuário
    user_input = """5Loved it!
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

    print("📊 Input do usuário:")
    print(repr(user_input))
    
    manager = ManualEpisodeManager()
    
    # Vamos fazer o debug manualmente
    import re
    
    lines = [line.strip() for line in user_input.strip().split('\n') if line.strip()]
    print(f"\n📋 Linhas processadas: {lines}")
    
    # Detectar ratings
    rating_starts = []
    for i, line in enumerate(lines):
        if (line and line[0].isdigit() and 
            int(line[0]) <= 5 and 
            len(line) > 1 and 
            any(c.isalpha() for c in line)):  # Tem texto após o número
            rating_starts.append(i)
            print(f"✅ Rating encontrado na linha {i}: '{line}'")
    
    print(f"\n🎯 Rating starts: {rating_starts}")
    print(f"📊 Total de linhas: {len(lines)}")
    print(f"📊 Total de ratings: {len(rating_starts)}")
    
    # Agrupar por rating
    rating_groups = []
    for i, start in enumerate(rating_starts):
        end = rating_starts[i + 1] if i + 1 < len(rating_starts) else len(lines)
        group_lines = lines[start:end]
        combined_line = ' '.join(group_lines)
        rating_groups.append(combined_line)
        print(f"📦 Grupo {i+1}: {group_lines} -> '{combined_line}'")
    
    print(f"\n🔢 CALCULANDO VOTOS:")
    total_votes = 0
    weighted_sum = 0
    
    for i, line in enumerate(rating_groups):
        if not line or not line[0].isdigit():
            continue
            
        rating_value = int(line[0])
        numbers = re.findall(r'\d+(?:\.\d+)?', line)
        
        print(f"📋 Linha {i+1}: '{line}'")
        print(f"   ⭐ Rating: {rating_value}")
        print(f"   🔢 Números encontrados: {numbers}")
        
        if len(numbers) >= 3:
            votes = int(float(numbers[-1]))
            print(f"   👥 Votos: {votes}")
            total_votes += votes
            weighted_sum += rating_value * votes
            print(f"   📊 Contribuição: {rating_value} x {votes} = {rating_value * votes}")
        
    print(f"\n📈 RESULTADO FINAL:")
    print(f"   Total de votos: {total_votes}")
    print(f"   Soma ponderada: {weighted_sum}")
    
    if total_votes > 0:
        average = weighted_sum / total_votes
        print(f"   Média: {weighted_sum} / {total_votes} = {average}")
        print(f"   Rating final: {round(average, 2)}")
    
    # Testar com o método oficial
    print(f"\n🧪 TESTE COM MÉTODO OFICIAL:")
    result = manager.parse_rating_data(user_input)
    print(f"   Resultado: {result}")

if __name__ == '__main__':
    debug_rating_calculation()