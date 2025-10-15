#!/usr/bin/env python3
"""
Teste e debug do parser de rating
"""

import re

def debug_parse_rating_data(rating_input: str) -> float:
    """
    Versão de debug do parser de rating
    """
    print(f"🔍 DEBUG: Input recebido:")
    print(f"'{rating_input}'")
    print(f"🔍 DEBUG: Tipo: {type(rating_input)}")
    print(f"🔍 DEBUG: Comprimento: {len(rating_input)}")
    
    try:
        lines = rating_input.strip().split('\n')
        print(f"🔍 DEBUG: Linhas após split: {lines}")
        
        total_votes = 0
        weighted_sum = 0
        
        for i, line in enumerate(lines):
            print(f"🔍 DEBUG: Linha {i}: '{line}'")
            
            if not line.strip():
                print(f"   -> Linha vazia, pulando")
                continue
                
            # Primeiro caractere é o rating (1-5)
            if not line[0].isdigit():
                print(f"   -> Primeiro caractere não é dígito: '{line[0]}', pulando")
                continue
                
            rating_value = int(line[0])
            print(f"   -> Rating value: {rating_value}")
            
            # Procurar por números na linha (porcentagem e votos)
            numbers = re.findall(r'\d+(?:\.\d+)?', line)
            print(f"   -> Números encontrados: {numbers}")
            
            if len(numbers) >= 2:
                # Último número é geralmente a quantidade de votos
                votes = int(float(numbers[-1]))
                print(f"   -> Votos: {votes}")
                total_votes += votes
                weighted_sum += rating_value * votes
            else:
                print(f"   -> Não há números suficientes na linha")
        
        print(f"🔍 DEBUG: Total de votos: {total_votes}")
        print(f"🔍 DEBUG: Soma ponderada: {weighted_sum}")
        
        if total_votes == 0:
            print(f"❌ DEBUG: Total de votos é 0")
            return 0.0
            
        # Calcular média ponderada e converter para escala MAL (1-10)
        average = weighted_sum / total_votes
        print(f"🔍 DEBUG: Média: {average}")
        
        mal_score = (average - 1) * 2.25 + 1  # Converte escala 1-5 para ~1-10
        print(f"🔍 DEBUG: Score MAL: {mal_score}")
        
        return round(mal_score, 2)
        
    except Exception as e:
        print(f"❌ Erro ao processar rating: {e}")
        import traceback
        traceback.print_exc()
        return 0.0

def test_rating_formats():
    """Testa diferentes formatos de rating"""
    
    print("🧪 TESTANDO DIFERENTES FORMATOS DE RATING")
    print("=" * 50)
    
    # Formato 1: Uma linha
    test1 = "5Loved it! 72.7% 197 4Liked it! 21.0% 57 3It was OK 4.8% 13 2Disliked it 0.4% 1 1Hated it 1.1% 3"
    print("\n📝 Teste 1 - Uma linha:")
    result1 = debug_parse_rating_data(test1)
    print(f"✅ Resultado: {result1}")
    
    # Formato 2: Múltiplas linhas (como no problema)
    test2 = """5Loved it!
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
    print("\n📝 Teste 2 - Múltiplas linhas separadas:")
    result2 = debug_parse_rating_data(test2)
    print(f"✅ Resultado: {result2}")
    
    # Formato 3: Uma linha por rating
    test3 = """5Loved it! 72.7% 197
4Liked it! 21.0% 57
3It was OK 4.8% 13
2Disliked it 0.4% 1
1Hated it 1.1% 3"""
    print("\n📝 Teste 3 - Uma linha por rating:")
    result3 = debug_parse_rating_data(test3)
    print(f"✅ Resultado: {result3}")

if __name__ == '__main__':
    test_rating_formats()