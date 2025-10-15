import sqlite3
import os
import requests
import time
from datetime import datetime
from typing import List, Dict, Any

class ManualEpisodeManager:
    def __init__(self):
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.db_path = os.path.join(os.path.dirname(self.script_dir), 'top10animes.db')
        self.pending_episodes = []
        
    def get_anime_info(self, anime_id: int) -> Dict[str, Any]:
        """Busca informações do anime na API do Jikan"""
        try:
            url = f"https://api.jikan.moe/v4/anime/{anime_id}"
            response = requests.get(url)
            response.raise_for_status()
            
            data = response.json()['data']
            
            return {
                'id': data['mal_id'],
                'title': data['title'],
                'title_english': data.get('title_english'),  # Adicionar título em inglês
                'image_url': data['images']['jpg']['large_image_url'],  # Usar large_image_url como no script automático
                'type': data['type'],
                'url': data['url']
            }
        except requests.exceptions.RequestException as e:
            print(f"❌ Erro ao buscar anime {anime_id}: {e}")
            return None
        except KeyError as e:
            print(f"❌ Dados do anime {anime_id} não encontrados: {e}")
            return None

    def parse_rating_data(self, rating_input: str) -> float:
        """
        Converte dados de rating de múltiplos formatos:
        
        Formato 1 - Uma linha por rating:
        5Loved it! 72.7% 197
        4Liked it! 21.0% 57
        
        Formato 2 - Linhas separadas:
        5Loved it!
        72.7%
        197
        4Liked it!
        21.0%
        57
        
        Para uma média ponderada na escala MAL (1.00-5.00)
        """
        try:
            import re
            
            # Primeiro, tentar detectar o formato
            lines = [line.strip() for line in rating_input.strip().split('\n') if line.strip()]
            
            # Detectar se está no formato separado (múltiplas linhas por rating)
            rating_groups = []
            
            # Verificar se temos linhas que começam com números 1-5 seguidos de texto
            rating_starts = []
            for i, line in enumerate(lines):
                if (line and line[0].isdigit() and 
                    int(line[0]) <= 5 and 
                    len(line) > 1 and 
                    any(c.isalpha() for c in line)):  # Tem texto após o número
                    rating_starts.append(i)
            
            # Se temos exatamente 5 ratings e mais linhas do que ratings, é formato separado
            if len(rating_starts) == 5 and len(lines) > 5:
                # Formato separado - agrupar por rating
                for i, start in enumerate(rating_starts):
                    end = rating_starts[i + 1] if i + 1 < len(rating_starts) else len(lines)
                    group_lines = lines[start:end]
                    combined_line = ' '.join(group_lines)
                    rating_groups.append(combined_line)
            else:
                # Formato padrão - uma linha por rating
                rating_groups = lines
            
            total_votes = 0
            weighted_sum = 0
            
            for line in rating_groups:
                if not line or not line[0].isdigit():
                    continue
                    
                rating_value = int(line[0])
                
                # Procurar por números na linha (rating, porcentagem, votos)
                numbers = re.findall(r'\d+(?:\.\d+)?', line)
                
                if len(numbers) >= 3:  # rating, porcentagem, votos
                    votes = int(float(numbers[-1]))  # Último número são os votos
                    total_votes += votes
                    weighted_sum += rating_value * votes
                elif len(numbers) >= 2:  # rating, votos (sem porcentagem)
                    votes = int(float(numbers[-1]))
                    total_votes += votes
                    weighted_sum += rating_value * votes
            
            if total_votes == 0:
                print("❌ Nenhum voto foi encontrado nos dados fornecidos")
                return 0.0
                
            # Calcular média ponderada (escala 1-5 do MAL)
            average = weighted_sum / total_votes
            
            # A média já está na escala correta 1.00-5.00 do MAL
            # 1 estrela = 1.00, 2 estrelas = 2.00, etc.
            mal_score = average
            
            return round(mal_score, 2)
            
        except Exception as e:
            print(f"❌ Erro ao processar rating: {e}")
            print("💡 Certifique-se de que os dados estão no formato correto:")
            print("   5Loved it! 72.7% 197")
            print("   4Liked it! 21.0% 57")
            print("   (etc...)")
            return 0.0

    def validate_episode_data(self, episode_data: Dict[str, Any]) -> bool:
        """Valida os dados do episódio"""
        required_fields = ['anime_id', 'episode_number', 'title', 'rating']
        
        for field in required_fields:
            if field not in episode_data or episode_data[field] is None:
                print(f"❌ Campo obrigatório ausente: {field}")
                return False
                
        if episode_data['rating'] <= 0:
            print("❌ Rating deve ser maior que 0")
            return False
            
        return True

    def check_duplicate_episode(self, anime_id: int, episode_number: int) -> bool:
        """Verifica se o episódio já existe no banco"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Verificar na tabela normal
        c.execute('SELECT id FROM episodes WHERE anime_id = ? AND episode_number = ?', 
                 (anime_id, episode_number))
        exists_normal = c.fetchone() is not None
        
        # Verificar na tabela manual
        c.execute('SELECT id FROM manual_episodes WHERE anime_id = ? AND episode_number = ?', 
                 (anime_id, episode_number))
        exists_manual = c.fetchone() is not None
        
        conn.close()
        return exists_normal or exists_manual

    def add_episode_to_cache(self) -> bool:
        """Adiciona um episódio ao cache temporário"""
        print("\n📝 Adicionando novo episódio manual")
        print("=" * 50)
        
        try:
            # 1. Solicitar anime ID
            while True:
                anime_id_input = input("🆔 Digite o Anime ID: ").strip()
                if not anime_id_input:
                    print("❌ Anime ID é obrigatório")
                    continue
                    
                try:
                    anime_id = int(anime_id_input)
                    break
                except ValueError:
                    print("❌ Anime ID deve ser um número")
                    
            # 2. Buscar informações do anime
            print("🔍 Buscando informações do anime...")
            anime_info = self.get_anime_info(anime_id)
            if not anime_info:
                print("❌ Não foi possível obter informações do anime")
                return False
                
            print(f"✅ Anime encontrado: {anime_info['title']} ({anime_info['type']})")
            time.sleep(0.5)  # Rate limiting
            
            # 3. Solicitar número do episódio
            while True:
                ep_number_input = input("📺 Digite o número do episódio: ").strip()
                if not ep_number_input:
                    print("❌ Número do episódio é obrigatório")
                    continue
                    
                try:
                    episode_number = int(ep_number_input)
                    break
                except ValueError:
                    print("❌ Número do episódio deve ser um número")
                    
            # 4. Verificar duplicatas
            if self.check_duplicate_episode(anime_id, episode_number):
                print(f"❌ Episódio {episode_number} do anime {anime_id} já existe no banco")
                return False
                
            # Verificar duplicatas no cache atual
            for cached_ep in self.pending_episodes:
                if (cached_ep['anime_id'] == anime_id and 
                    cached_ep['episode_number'] == episode_number):
                    print(f"❌ Episódio {episode_number} já está no cache para processamento")
                    return False
            
            # 5. Solicitar nome do episódio
            episode_title = input("📝 Digite o nome do episódio: ").strip()
            if not episode_title:
                print("❌ Nome do episódio é obrigatório")
                return False
                
            # 6. Solicitar data de lançamento
            while True:
                air_date_input = input("📅 Digite a data que o episódio foi ao ar (YYYY-MM-DD): ").strip()
                if not air_date_input:
                    print("❌ Data de lançamento é obrigatória")
                    continue
                    
                # Validar formato da data
                try:
                    from datetime import datetime
                    datetime.strptime(air_date_input, '%Y-%m-%d')
                    air_date = air_date_input
                    break
                except ValueError:
                    print("❌ Formato de data inválido. Use YYYY-MM-DD (ex: 2025-10-15)")
                    
            # 7. Solicitar dados de rating
            print("\n⭐ Cole os dados de rating do MyAnimeList:")
            print("💡 Formatos aceitos:")
            print("   📄 Formato 1 - Uma linha por rating:")
            print("      5Loved it! 72.7% 197")
            print("      4Liked it! 21.0% 57")
            print("   📄 Formato 2 - Linhas separadas (copie e cole direto):")
            print("      5Loved it!")
            print("      72.7%")
            print("      197")
            print("   ✅ Ambos funcionam perfeitamente!")
            print("   🔚 Pressione Enter duas vezes quando terminar")
            
            rating_lines = []
            empty_count = 0
            while True:
                line = input()
                if line.strip() == "":
                    empty_count += 1
                    if empty_count >= 2 or (rating_lines and empty_count >= 1):  # Duas linhas vazias ou uma se já tem dados
                        break
                else:
                    empty_count = 0
                    rating_lines.append(line)
                
            rating_input = '\n'.join(rating_lines)  # Manter quebras de linha para processar corretamente
            if not rating_input.strip():
                print("❌ Dados de rating são obrigatórios")
                return False
                
            # 8. Calcular rating
            calculated_rating = self.parse_rating_data(rating_input)
            if calculated_rating <= 0:
                print("❌ Não foi possível calcular o rating")
                return False
                
            print(f"📊 Rating calculado: {calculated_rating}")
            
            # 9. Criar dados do episódio seguindo exato padrão do script automático
            # Usar título em inglês como preferência, igual ao script automático
            anime_display_title = anime_info.get('title_english') or anime_info['title']
            
            # Formatar título do episódio exatamente como o script automático
            formatted_episode_title = f"EP {episode_number} • {episode_title}"
            
            # Construir URL do episódio seguindo padrão automático
            import math
            url_anime_title_for_mal = anime_display_title.replace(' ', '_')
            offset = math.floor((episode_number - 1) / 100) * 100
            episode_url = f"https://myanimelist.net/anime/{anime_id}/{url_anime_title_for_mal}/episode?offset={offset}"
            
            episode_data = {
                'anime_id': anime_id,
                'episode_number': episode_number,
                'title': formatted_episode_title,  # Título formatado igual aos automáticos
                'rating': calculated_rating,
                'anime_title': anime_display_title,  # Título preferido (inglês ou padrão)
                'anime_image_url': anime_info['image_url'],  # Já é large_image_url
                'episode_url': episode_url,  # URL com padrão correto e offset
                'anime_type': anime_info['type'],
                'air_date': air_date,
                'raw_rating_data': rating_input
            }
            
            # 10. Validar dados
            if not self.validate_episode_data(episode_data):
                return False
                
            # 11. Adicionar ao cache
            self.pending_episodes.append(episode_data)
            
            print(f"✅ Episódio '{episode_title}' adicionado ao cache!")
            print(f"📦 Total no cache: {len(self.pending_episodes)} episódio(s)")
            
            return True
            
        except KeyboardInterrupt:
            print("\n❌ Operação cancelada pelo usuário")
            return False
        except Exception as e:
            print(f"❌ Erro inesperado: {e}")
            return False

    def show_cache_summary(self):
        """Mostra resumo dos episódios no cache"""
        if not self.pending_episodes:
            print("📦 Cache vazio")
            return
            
        print(f"\n📦 RESUMO DO CACHE ({len(self.pending_episodes)} episódios)")
        print("=" * 60)
        
        for i, ep in enumerate(self.pending_episodes, 1):
            print(f"{i}. {ep['anime_title']}")
            print(f"   📺 {ep['title']}")  # Já contém o formato "EP X • Nome"
            print(f"   ⭐ Rating: {ep['rating']}")
            print(f"   📅 Data de lançamento: {ep['air_date']}")
            print(f"   🔗 URL: {ep['episode_url']}")
            print(f"   🆔 Anime ID: {ep['anime_id']}")
            print()

    def save_episodes_to_database(self) -> bool:
        """Salva todos os episódios do cache no banco de dados"""
        if not self.pending_episodes:
            print("❌ Nenhum episódio no cache para salvar")
            return False
            
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            current_time = datetime.now().isoformat()
            saved_count = 0
            
            for episode in self.pending_episodes:
                # Gerar ID único
                episode_id = f"manual_{episode['anime_id']}_{episode['episode_number']}"
                
                # Verificar duplicatas uma última vez
                c.execute('SELECT id FROM episodes WHERE anime_id = ? AND episode_number = ?', 
                         (episode['anime_id'], episode['episode_number']))
                if c.fetchone():
                    print(f"⚠️ Pulando episódio duplicado: {episode['anime_title']} EP{episode['episode_number']}")
                    continue
                    
                c.execute('SELECT id FROM manual_episodes WHERE anime_id = ? AND episode_number = ?', 
                         (episode['anime_id'], episode['episode_number']))
                if c.fetchone():
                    print(f"⚠️ Pulando episódio duplicado: {episode['anime_title']} EP{episode['episode_number']}")
                    continue
                
                # Inserir no banco
                c.execute('''
                    INSERT INTO manual_episodes 
                    (id, anime_id, title, episode_number, rating, anime_title, 
                     anime_image_url, episode_url, anime_type, date_added, air_date, is_manual)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
                ''', (
                    episode_id,
                    episode['anime_id'],
                    episode['title'],
                    episode['episode_number'],
                    episode['rating'],
                    episode['anime_title'],
                    episode['anime_image_url'],
                    episode['episode_url'],
                    episode['anime_type'],
                    current_time,
                    episode['air_date']
                ))
                
                saved_count += 1
                print(f"✅ Salvo: {episode['anime_title']} EP{episode['episode_number']}")
            
            conn.commit()
            conn.close()
            
            print(f"\n🎉 {saved_count} episódio(s) salvo(s) com sucesso!")
            
            # Limpar cache
            self.pending_episodes.clear()
            
            return True
            
        except Exception as e:
            print(f"❌ Erro ao salvar no banco: {e}")
            return False

    def show_main_menu(self):
        """Mostra o menu principal"""
        print("\n🎬 SISTEMA DE ADIÇÃO MANUAL DE EPISÓDIOS")
        print("=" * 50)
        print(f"📦 Cache atual: {len(self.pending_episodes)} episódio(s)")
        print()
        print("1️⃣  Adicionar episódio ao cache")
        print("2️⃣  Ver resumo do cache")
        print("3️⃣  Salvar todos no banco de dados")
        print("4️⃣  Limpar cache")
        print("0️⃣  Sair")
        print()

    def run(self):
        """Executa o sistema interativo"""
        print("🎬 Bem-vindo ao Sistema de Adição Manual de Episódios!")
        
        while True:
            self.show_main_menu()
            
            try:
                choice = input("👆 Escolha uma opção: ").strip()
                
                if choice == '1':
                    self.add_episode_to_cache()
                    
                elif choice == '2':
                    self.show_cache_summary()
                    
                elif choice == '3':
                    if not self.pending_episodes:
                        print("❌ Cache vazio! Adicione episódios primeiro.")
                        continue
                        
                    self.show_cache_summary()
                    confirm = input("\n❓ Confirma salvar todos os episódios? (s/N): ").strip().lower()
                    if confirm == 's':
                        if self.save_episodes_to_database():
                            print("🎉 Operação concluída!")
                        else:
                            print("❌ Erro ao salvar episódios")
                    else:
                        print("❌ Operação cancelada")
                        
                elif choice == '4':
                    if self.pending_episodes:
                        confirm = input(f"❓ Confirma limpar {len(self.pending_episodes)} episódio(s) do cache? (s/N): ").strip().lower()
                        if confirm == 's':
                            self.pending_episodes.clear()
                            print("🗑️ Cache limpo!")
                        else:
                            print("❌ Operação cancelada")
                    else:
                        print("📦 Cache já está vazio")
                        
                elif choice == '0':
                    if self.pending_episodes:
                        print(f"\n⚠️ Você tem {len(self.pending_episodes)} episódio(s) no cache!")
                        confirm = input("❓ Tem certeza que deseja sair sem salvar? (s/N): ").strip().lower()
                        if confirm != 's':
                            continue
                            
                    print("👋 Até logo!")
                    break
                    
                else:
                    print("❌ Opção inválida")
                    
            except KeyboardInterrupt:
                print("\n\n👋 Saindo...")
                break
            except Exception as e:
                print(f"❌ Erro inesperado: {e}")

if __name__ == '__main__':
    manager = ManualEpisodeManager()
    manager.run()