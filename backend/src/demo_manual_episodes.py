#!/usr/bin/env python3
"""
Demo do Sistema de Adição Manual de Episódios
Demonstra como usar o sistema para adicionar episódios que não estão disponíveis na API
"""

def demo_rating_calculation():
    """Demonstra o cálculo de rating"""
    from manual_episodes import ManualEpisodeManager
    
    print("🧮 DEMO: Cálculo de Rating")
    print("=" * 40)
    
    manager = ManualEpisodeManager()
    
    # Exemplo de dados de rating
    rating_data = """5Loved it! 72.7% 197
4Liked it! 21.0% 57
3It was OK 4.8% 13
2Disliked it 0.4% 1
1Hated it 1.1% 3"""
    
    print("📊 Dados de entrada:")
    print(rating_data)
    print()
    
    calculated_rating = manager.parse_rating_data(rating_data)
    
    print(f"📈 Rating calculado: {calculated_rating}")
    print(f"💡 Método: Média ponderada na escala MAL (1.00-5.00)")
    
    return calculated_rating

def show_usage_guide():
    """Mostra guia de uso do sistema"""
    print("\n📖 GUIA DE USO DO SISTEMA")
    print("=" * 50)
    print("1️⃣ Execute: python manual_episodes.py")
    print("2️⃣ Escolha opção 1 para adicionar episódios")
    print("3️⃣ Para cada episódio, forneça:")
    print("   • 🆔 Anime ID (ex: 21 para One Piece)")
    print("   • 📺 Número do episódio")
    print("   • 📝 Nome do episódio")
    print("   • ⭐ Dados de rating (cole o formato do MAL)")
    print("4️⃣ Repita para quantos episódios precisar")
    print("5️⃣ Use opção 2 para ver resumo do cache")
    print("6️⃣ Use opção 3 para salvar tudo no banco")
    print("7️⃣ Execute export_data.py para gerar JSON")
    print()
    print("🔧 Episódios manuais aparecem com ícone 🔧 no frontend")
    print()

def show_example_workflow():
    """Mostra um exemplo completo de workflow"""
    print("💡 EXEMPLO DE WORKFLOW")
    print("=" * 30)
    print("Cenário: Episódio de 'A Wild Last Boss Appeared!' ainda")
    print("não está na API, mas você quer incluí-lo no ranking")
    print()
    print("1️⃣ Encontre o Anime ID no MAL: 59027")
    print("2️⃣ Identifique o episódio: EP 2")
    print("3️⃣ Copie os dados de rating do MAL:")
    print("   5Loved it! 72.7% 197")
    print("   4Liked it! 21.0% 57")
    print("   3It was OK 4.8% 13")
    print("   2Disliked it 0.4% 1")
    print("   1Hated it 1.1% 3")
    print("4️⃣ Execute o sistema e cole os dados")
    print("5️⃣ Sistema calcula rating automaticamente")
    print("6️⃣ Salve no banco e exporte para frontend")
    print()

if __name__ == '__main__':
    print("🎬 DEMONSTRAÇÃO - SISTEMA DE EPISÓDIOS MANUAIS")
    print("=" * 55)
    
    # Demo do cálculo
    demo_rating_calculation()
    
    # Guia de uso
    show_usage_guide()
    
    # Exemplo de workflow
    show_example_workflow()
    
    print("🚀 SISTEMA PRONTO PARA USO!")
    print("Execute: python manual_episodes.py")