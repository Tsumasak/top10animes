"""
Script de teste e migração para a API Jikan.
Este script testa as principais funcionalidades da nova API.
"""

import json
from jikan_api import (
    get_anticipated_animes, 
    get_seasonal_animes_jikan, 
    get_top_anime_by_score, 
    search_anime,
    get_anime_details
)

def test_seasonal_animes():
    """Testa a busca de animes sazonais."""
    print("\n" + "="*60)
    print("TESTE: Animes Sazonais")
    print("="*60)
    
    try:
        animes = get_seasonal_animes_jikan(2024, "fall", limit=5, min_members=10000)
        print(f"✓ Encontrados {len(animes)} animes da temporada Fall 2024")
        
        for i, anime in enumerate(animes[:3], 1):
            print(f"{i}. {anime['title']}")
            print(f"   Score: {anime['score']}, Membros: {anime['members']:,}")
            print(f"   Status: {anime['status']}")
        
        return True
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def test_anticipated_animes():
    """Testa a busca de animes mais esperados."""
    print("\n" + "="*60)
    print("TESTE: Animes Mais Esperados")
    print("="*60)
    
    try:
        animes = get_anticipated_animes()
        print(f"✓ Encontrados {len(animes)} animes mais esperados")
        
        for i, anime in enumerate(animes[:3], 1):
            print(f"{i}. {anime['title']}")
            print(f"   Score: {anime['score']}, Membros: {anime['members_count']:,}")
            print(f"   Ranking: {anime['ranking']}")
        
        return True
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def test_top_animes():
    """Testa a busca dos melhores animes por score."""
    print("\n" + "="*60)
    print("TESTE: Top Animes por Score")
    print("="*60)
    
    try:
        animes = get_top_anime_by_score(limit=5, min_score=8.0)
        print(f"✓ Encontrados {len(animes)} top animes")
        
        for anime in animes[:3]:
            print(f"{anime['ranking']}. {anime['title']}")
            print(f"   Score: {anime['score']} ({anime['scored_by']:,} votos)")
            print(f"   Membros: {anime['members']:,}")
        
        return True
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def test_search():
    """Testa a busca por anime específico."""
    print("\n" + "="*60)
    print("TESTE: Busca por Anime")
    print("="*60)
    
    try:
        results = search_anime("Demon Slayer", limit=3)
        print(f"✓ Encontrados {len(results)} resultados para 'Demon Slayer'")
        
        for result in results:
            print(f"• {result['title']}")
            print(f"  Score: {result['score']}, Episódios: {result['episodes']}")
            print(f"  Ano: {result['year']}, Status: {result['status']}")
        
        return True
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def test_anime_details():
    """Testa a busca de detalhes específicos."""
    print("\n" + "="*60)
    print("TESTE: Detalhes do Anime")
    print("="*60)
    
    try:
        # Teste com Cowboy Bebop (ID: 1)
        details = get_anime_details(1)
        if details:
            print(f"✓ Detalhes obtidos para: {details['title']}")
            print(f"   Score: {details['score']}")
            print(f"   Membros: {details['members']:,}")
            print(f"   Gêneros: {', '.join(details['genres'][:3])}")
            print(f"   Estúdios: {', '.join(details['studios'])}")
        
        return True
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def compare_with_backup():
    """Compara funcionalidades antigas vs novas."""
    print("\n" + "="*60)
    print("COMPARAÇÃO: Funcionalidades Antigas vs Novas")
    print("="*60)
    
    print("ANTES (MAL API Oficial):")
    print("• Requeria autenticação OAuth")
    print("• Tokens de acesso com expiração")
    print("• Limitado em informações de score")
    print("• Rate limit mais restritivo")
    
    print("\nDEPOIS (Jikan API):")
    print("✓ Sem necessidade de autenticação")
    print("✓ Acesso completo a scores e ratings")
    print("✓ Mais informações sobre animes")
    print("✓ Rate limit mais generoso")
    print("✓ Funcionalidades extras (top por score, busca avançada)")

def run_migration_tests():
    """Executa todos os testes de migração."""
    print("="*80)
    print("|| TESTES DE MIGRAÇÃO - API MAL PARA JIKAN ||")
    print("="*80)
    
    tests = [
        ("Animes Sazonais", test_seasonal_animes),
        ("Animes Esperados", test_anticipated_animes),
        ("Top Animes", test_top_animes),
        ("Busca", test_search),
        ("Detalhes", test_anime_details)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ Falha crítica no teste {test_name}: {e}")
    
    compare_with_backup()
    
    print("\n" + "="*80)
    print("|| RESULTADO DOS TESTES ||")
    print("="*80)
    print(f"Testes passaram: {passed}/{total}")
    
    if passed == total:
        print("✓ MIGRAÇÃO BEM-SUCEDIDA!")
        print("✓ Todas as funcionalidades estão operacionais")
        print("✓ A API Jikan está pronta para uso")
    else:
        print("⚠ MIGRAÇÃO PARCIAL")
        print("Algumas funcionalidades podem precisar de ajustes")
    
    print("\nBackup disponível na pasta 'backup/' para reverter se necessário")

if __name__ == "__main__":
    run_migration_tests()