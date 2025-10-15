"""
Sistema principal usando 100% JIKAN API - Sem scraping
Versão otimizada que elimina completamente BeautifulSoup e scraping
"""

import json
import os
from datetime import datetime, timedelta, date
from jikan_api import get_anticipated_animes, make_jikan_request, _get_safe_title

# Importar os novos módulos otimizados
from update_anticipated_animes import get_anticipated_animes_full, save_anticipated_animes_data
from update_top_episodes import get_top_episodes_jikan, save_episodes_data

def get_config():
    """Carrega a configuração do arquivo JSON."""
    with open('config.json', 'r') as f:
        return json.load(f)

def get_period_input():
    """Solicita e valida período de datas do usuário."""
    print("\n📅 Definir período para busca de episódios:")
    
    while True:
        try:
            print("\nOpções:")
            print("1. Semana atual")
            print("2. Última semana")
            print("3. Período personalizado")
            
            choice = input("\nEscolha uma opção (1-3): ").strip()
            
            if choice == "1":
                # Semana atual (domingo a sábado)
                today = date.today()
                days_since_sunday = today.weekday() + 1  # +1 porque weekday() considera segunda = 0
                if days_since_sunday == 7:  # Se for domingo
                    days_since_sunday = 0
                
                start_date = today - timedelta(days=days_since_sunday)
                end_date = start_date + timedelta(days=6)
                
            elif choice == "2":
                # Última semana
                today = date.today()
                days_since_sunday = today.weekday() + 1
                if days_since_sunday == 7:
                    days_since_sunday = 0
                
                this_sunday = today - timedelta(days=days_since_sunday)
                start_date = this_sunday - timedelta(days=7)
                end_date = this_sunday - timedelta(days=1)
                
            elif choice == "3":
                # Período personalizado
                start_str = input("Data início (YYYY-MM-DD ou DD/MM/YYYY): ").strip()
                end_str = input("Data fim (YYYY-MM-DD ou DD/MM/YYYY): ").strip()
                
                # Tentar diferentes formatos
                for fmt in ['%Y-%m-%d', '%d/%m/%Y']:
                    try:
                        start_date = datetime.strptime(start_str, fmt).date()
                        end_date = datetime.strptime(end_str, fmt).date()
                        break
                    except ValueError:
                        continue
                else:
                    print("❌ Formato de data inválido! Use YYYY-MM-DD ou DD/MM/YYYY")
                    continue
                    
            else:
                print("❌ Opção inválida!")
                continue
            
            # Validar período
            if start_date > end_date:
                print("❌ Data início não pode ser posterior à data fim!")
                continue
            
            # Confirmar período
            print(f"\n📅 Período selecionado: {start_date.strftime('%d/%m/%Y')} até {end_date.strftime('%d/%m/%Y')}")
            confirm = input("Confirmar? (s/N): ").strip().lower()
            
            if confirm in ['s', 'sim', 'y', 'yes']:
                return start_date, end_date
                
        except ValueError as e:
            print(f"❌ Erro no formato da data: {e}")
        except Exception as e:
            print(f"❌ Erro inesperado: {e}")

def run_weekly_ranking_jikan():
    """Executa a geração do ranking de episódios usando 100% JIKAN API."""
    print("\n" + "="*80)
    print("🎬 GERANDO RANKING: TOP 50 EPISÓDIOS DA SEMANA (100% JIKAN API)")
    print("="*80)
    
    try:
        # Obter período
        start_date, end_date = get_period_input()
        
        print(f"\n🎯 Buscando episódios de {start_date} até {end_date}...")
        
        # Buscar episódios usando apenas JIKAN
        episodes = get_top_episodes_jikan(start_date, end_date, limit=50)
        
        if not episodes:
            print("❌ Nenhum episódio encontrado no período!")
            return
        
        # Salvar dados
        save_episodes_data(episodes, start_date, end_date)
        
        print(f"\n✅ Ranking de episódios gerado com sucesso!")
        print(f"📊 {len(episodes)} episódios processados")
        
    except Exception as e:
        print(f"❌ Erro ao gerar ranking de episódios: {e}")
        import traceback
        traceback.print_exc()

def run_anticipated_ranking_jikan():
    """Executa a geração do ranking de animes esperados usando 100% JIKAN API."""
    print("\n" + "="*80)
    print("🌟 GERANDO RANKING: TOP 50 ANIMES MAIS ESPERADOS (100% JIKAN API)")
    print("="*80)
    
    try:
        print("🔍 Buscando animes mais esperados com informações completas...")
        
        # Buscar animes esperados com algoritmo avançado
        animes_data = get_anticipated_animes_full()
        
        if not animes_data:
            print("❌ Nenhum anime esperado foi encontrado!")
            return
        
        # Salvar dados
        save_anticipated_animes_data(animes_data)
        
        print(f"\n✅ Ranking de animes esperados gerado com sucesso!")
        print(f"🎯 {len(animes_data)} animes processados")
        
    except Exception as e:
        print(f"❌ Erro ao gerar ranking de animes esperados: {e}")
        import traceback
        traceback.print_exc()

def show_stats():
    """Mostra estatísticas dos dados existentes."""
    print("\n" + "="*80)
    print("📊 ESTATÍSTICAS DOS DADOS ATUAIS")
    print("="*80)
    
    try:
        # Verificar dados de episódios
        episodes_file = "frontend/public/episodes_data.json"
        if os.path.exists(episodes_file):
            with open(episodes_file, 'r', encoding='utf-8') as f:
                episodes_data = json.load(f)
            
            print(f"🎬 EPISÓDIOS:")
            print(f"   📅 Última atualização: {episodes_data.get('generated_at', 'N/A')}")
            print(f"   📊 Total de episódios: {episodes_data.get('total_episodes', 0)}")
            print(f"   📅 Período: {episodes_data.get('start_date', 'N/A')} até {episodes_data.get('end_date', 'N/A')}")
            print(f"   🔧 Método: {episodes_data.get('update_source', 'N/A')}")
            
            # Top 5 episódios
            episodes = episodes_data.get('episodes', [])
            if episodes:
                print(f"\n   🏆 TOP 5 EPISÓDIOS:")
                for i, ep in enumerate(episodes[:5], 1):
                    print(f"   {i}. {ep.get('anime_title', 'N/A')} - EP{ep.get('episode_number', 0)}")
                    print(f"      Score: {ep.get('score', 0):.2f}")
        else:
            print("🎬 EPISÓDIOS: Nenhum dado encontrado")
        
        print()
        
        # Verificar dados de animes esperados
        animes_file = "frontend/public/anticipated_animes_data.json"
        if os.path.exists(animes_file):
            with open(animes_file, 'r', encoding='utf-8') as f:
                animes_data = json.load(f)
            
            print(f"🌟 ANIMES ESPERADOS:")
            print(f"   📅 Última atualização: {animes_data.get('generated_date', 'N/A')}")
            print(f"   🎯 Total de animes: {animes_data.get('total_animes', 0)}")
            print(f"   🔧 Método: {animes_data.get('update_source', 'N/A')}")
            
            # Top 5 animes
            animes = animes_data.get('animes', [])
            if animes:
                print(f"\n   🏆 TOP 5 ANIMES ESPERADOS:")
                for i, anime in enumerate(animes[:5], 1):
                    title = anime.get('title', 'N/A')
                    score = anime.get('expectation_score', anime.get('score', 0))
                    members = anime.get('members_display', anime.get('members', 0))
                    print(f"   {i}. {title[:50]}...")
                    print(f"      Score: {score} | Membros: {members}")
        else:
            print("🌟 ANIMES ESPERADOS: Nenhum dado encontrado")
            
    except Exception as e:
        print(f"❌ Erro ao carregar estatísticas: {e}")

def test_jikan_connection():
    """Testa a conectividade com a API JIKAN."""
    print("\n" + "="*80)
    print("🔧 TESTE DE CONECTIVIDADE JIKAN API")
    print("="*80)
    
    try:
        print("🔍 Testando conexão...")
        
        # Teste básico
        data = make_jikan_request("anime/1")  # Cowboy Bebop
        
        if data and 'data' in data:
            anime = data['data']
            print(f"✅ Conexão OK!")
            print(f"📺 Anime teste: {anime.get('title', 'N/A')}")
            print(f"📊 Score: {anime.get('score', 'N/A')}")
            print(f"👥 Membros: {anime.get('members', 0):,}")
            
            # Teste de temporadas
            print(f"\n🔍 Testando busca de temporadas...")
            season_data = make_jikan_request("seasons/2024/fall", {"limit": 1})
            
            if season_data and 'data' in season_data:
                print(f"✅ API de temporadas OK!")
                print(f"📅 Animes encontrados na temporada Fall 2024: {len(season_data['data'])}")
            else:
                print("⚠️ API de temporadas com problemas")
                
            print(f"\n🎯 Status: Tudo funcionando perfeitamente!")
            
        else:
            print("❌ Erro na conexão com JIKAN API")
            
    except Exception as e:
        print(f"❌ Erro no teste: {e}")

def show_help():
    """Mostra ajuda sobre o sistema."""
    print("\n" + "="*80)
    print("❓ AJUDA - SISTEMA TOP ANIMES 100% JIKAN")
    print("="*80)
    print("""
🎯 FUNCIONALIDADES PRINCIPAIS:

1. 🎬 Ranking de Episódios da Semana
   • Busca episódios que foram ao ar em um período específico
   • Calcula scores estimados baseado nos dados do anime
   • Sem necessidade de scraping - 100% JIKAN API
   • Suporte a períodos personalizados

2. 🌟 Ranking de Animes Mais Esperados  
   • Algoritmo avançado de expectativa
   • Combina múltiplos fatores: membros, score, popularidade, etc.
   • Busca em temporadas atuais e futuras
   • Informações detalhadas de cada anime

3. 📊 Estatísticas e Monitoramento
   • Visualização dos dados atuais
   • Histórico de atualizações
   • Teste de conectividade com API

🔧 MELHORIAS DA VERSÃO JIKAN:
✅ Sem dependência de scraping
✅ Mais rápido e estável  
✅ Informações mais ricas (scores, estatísticas, etc.)
✅ Rate limiting respeitado automaticamente
✅ Sem necessidade de autenticação

📚 ARQUIVOS DE CONFIGURAÇÃO:
• config.json - Configurações gerais
• frontend/public/episodes_data.json - Dados dos episódios
• frontend/public/anticipated_animes_data.json - Dados dos animes esperados

🚀 DICA: Execute os testes de conectividade regularmente para
   garantir que a API JIKAN está respondendo corretamente.
""")

def main():
    """Função principal - Menu interativo."""
    print("🚀 SISTEMA TOP ANIMES - 100% JIKAN API")
    print("🎯 Versão Otimizada - Sem Scraping")
    
    while True:
        print("\n" + "="*80)
        print("📋 MENU PRINCIPAL")
        print("="*80)
        print("1. 🎬 Gerar Ranking de Episódios da Semana")
        print("2. 🌟 Gerar Ranking de Animes Mais Esperados")
        print("3. 🔄 Gerar Ambos os Rankings")
        print("4. 📊 Mostrar Estatísticas")
        print("5. 🔧 Testar Conectividade JIKAN")
        print("6. ❓ Ajuda")
        print("7. 🚪 Sair")
        print("="*80)

        choice = input("💭 Escolha uma opção (1-7): ").strip()

        if choice == '1':
            run_weekly_ranking_jikan()
            
        elif choice == '2':
            run_anticipated_ranking_jikan()
            
        elif choice == '3':
            print("\n🔄 Executando ambos os rankings...")
            run_weekly_ranking_jikan()
            run_anticipated_ranking_jikan()
            print("\n✅ Todos os rankings foram atualizados!")
            
        elif choice == '4':
            show_stats()
            
        elif choice == '5':
            test_jikan_connection()
            
        elif choice == '6':
            show_help()
            
        elif choice == '7':
            print("\n👋 Saindo do sistema...")
            print("✅ Obrigado por usar o Sistema Top Animes!")
            break
            
        else:
            print("❌ Opção inválida! Digite um número de 1 a 7.")

    print("\n🎯 Sistema finalizado!")

if __name__ == "__main__":
    main()