import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import time
import json
import os

# Funções de utilidade
from scraper_utils import debug_print, log_error, parse_air_date

# Funções do scraper de animes esperados
from mal_api import get_anticipated_animes, get_seasonal_animes

# --- BLOCO DE FUNÇÕES DE COLETA DE DADOS (SEMANAL) ---

def get_current_season():
    """Determina o ano e a estação atual."""
    d = datetime.now()
    if 1 <= d.month <= 3:
        return d.year, "winter"
    if 4 <= d.month <= 6:
        return d.year, "spring"
    if 7 <= d.month <= 9:
        return d.year, "summer"
    return d.year, "fall"

def get_episodes_info(anime_url, start_date, end_date, api_anime_title):
    try:
        episodes_url = anime_url.rstrip('/') + '/episode'
        debug_print(f"Acessando pßgina de episdios: {episodes_url}", 3)
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(episodes_url, headers=headers)
        if response.status_code == 404:
            debug_print(f"Pßgina de episdios nÒo encontrada (404): {episodes_url}", 2)
            return None
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        # Usar o título do anime passado via API, em vez de raspar
        anime_title = api_anime_title
        episode_table = soup.find('table', class_='episode_list')
        if not episode_table:
            debug_print(f"Tabela de episdios nÒo encontrada para {anime_title}", 2)
            return None
        rows = episode_table.find_all('tr', class_='episode-list-data')
        debug_print(f"Encontradas {len(rows)} linhas de episdios para {anime_title}", 3)
        episodes = []
        for row in rows:
            date_str = row.find('td', class_='episode-aired').text.strip()
            airdate = parse_air_date(date_str)
            debug_print(f"  Processando episdio: Data string='{date_str}', Airdate={airdate}", 4)
            if not airdate:
                debug_print(f"    Data de lanamento nÒo prseavel para '{date_str}'. Ignorando.", 4)
                continue
            if not (start_date <= airdate <= end_date):
                debug_print(f"    Episdio com data {airdate} fora do perodo {start_date} a {end_date}. Ignorando.", 4)
                continue
            score_td = row.find('td', class_='episode-poll')
            score = float(score_td.get('data-raw', '0')) if score_td and 'scored' in score_td.get('class', []) else 0.0
            episodes.append({
                'anime_title': anime_title,
                'episode_number': row.find('td', class_='episode-number').text.strip(),
                'episode_title': row.find('td', class_='episode-title').a.text.strip(),
                'score': score,
                'airdate': airdate
            })
        return episodes
    except Exception as e:
        log_error(e)
        return None

def save_data_to_json(episodes, filename='episodes_data.json'):
    """Salva os dados dos episódios em JSON para reuso"""
    data = {
        'generated_at': datetime.now().isoformat(),
        'episodes': episodes
    }
    with open(f"frontend/public/{filename}", 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)

# --- BLOCO DO RANKING SEMANAL ---

def run_weekly_ranking():
    """Executa a geração do ranking de episódios da semana (abordagem híbrida)."""
    print("\n" + "="*60)
    print("GERANDO RANKING: TOP 50 EPISÓDIOS DA SEMANA (HÍBRIDO API+SCRAPER)")
    print("="*60)
    try:
        # Solicitar datas ao usuário
        while True:
            start_date_str = input("Digite a data de início do período (DD/MM/AAAA): ")
            end_date_str = input("Digite a data de fim do período (DD/MM/AAAA): ")
            try:
                start_of_week = datetime.strptime(start_date_str, "%d/%m/%Y").date()
                end_of_week = datetime.strptime(end_date_str, "%d/%m/%Y").date()
                if start_of_week > end_of_week:
                    print("Erro: A data de início não pode ser posterior à data de fim. Tente novamente.")
                else:
                    break
            except ValueError:
                print("Erro: Formato de data inválido. Use DD/MM/AAAA. Tente novamente.")

        year, season = get_current_season()
        # 1. Usar a API para buscar a lista de animes da temporada
        anime_list = get_seasonal_animes(year, season)
        
        if not anime_list:
            debug_print("Nenhum anime encontrado via API para o ranking semanal.", 1)
            return
            
        debug_print(f"Período de referência: {start_of_week.strftime('%d/%m')} a {end_of_week.strftime('%d/%m')}", 1)
        all_episodes = []
        
        # 2. Usar o scraper para buscar os scores de cada anime
        for i, anime in enumerate(anime_list):
            title_for_print = anime['title'].encode('cp1252', 'replace').decode('cp1252')
            debug_print(f"Processando anime {i+1}/{len(anime_list)}: {title_for_print}", 1)
            
            # Chamada ao scraper mantida para buscar scores
            episodes = get_episodes_info(anime['url'], start_of_week, end_of_week, anime['title']) 
            
            if episodes:
                for ep in episodes:
                    ep['image'] = anime['image']
                    ep['url'] = anime['url']
                all_episodes.extend(episodes)
                debug_print(f"Encontrados {len(episodes)} episódios para '{title_for_print}' no período.", 2)
            time.sleep(0.1) # Manter a pausa para não sobrecarregar o servidor com o scraping
        
        if not all_episodes:
            print("Nenhum episódio encontrado no período de referência.")
            return

        episodes_with_score = sorted([ep for ep in all_episodes if ep['score'] > 0], key=lambda x: x['score'], reverse=True)
        top_50_episodes = episodes_with_score[:50]
        
        save_data_to_json(top_50_episodes, filename='episodes_data.json')
        print("Ranking de episódios da semana gerado com sucesso!")
    except Exception as e:
        print(f"Erro ao gerar ranking semanal: {e}")
        log_error(e)

def save_anticipated_animes_data(animes_data, output_path="./"):
    """Salva os dados dos animes esperados em JSON"""
    output_data = {
        'generated_date': datetime.now().isoformat(),
        'season': 'Fall 2025',
        'total_animes': len(animes_data),
        'animes': animes_data
    }
    
    # Garante que o diretório de saída exista
    os.makedirs(output_path, exist_ok=True)

    with open(os.path.join(output_path, 'anticipated_animes_data.json'), 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    debug_print(f"Dados salvos: {len(animes_data)} animes mais esperados em '{output_path}'", 1)
    return output_data

# --- BLOCO DO RANKING DE MAIS ESPERADOS ---

def run_anticipated_ranking():
    """Executa a geração do ranking de animes mais esperados via API."""
    print("\n" + "="*60)
    print("GERANDO RANKING: TOP 50 ANIMES MAIS ESPERADOS (VIA API)")
    print("="*60)
    try:
        animes_data = get_anticipated_animes()
        if not animes_data:
            print("Nenhum dado de animes esperados foi coletado pela API.")
            return
        save_anticipated_animes_data(animes_data, output_path="frontend/public/")
        print("Ranking de animes mais esperados gerado com sucesso!")
    except Exception as e:
        print(f"Erro ao gerar ranking de animes esperados: {e}")
        log_error(e)

# --- EXECUÇÃO PRINCIPAL ---

def main():
    """Função principal que executa ambos os rankings."""
    print("INICIANDO SISTEMA DE RANKINGS")

    while True:
        print("\n" + "="*60)
        print("MENU PRINCIPAL")
        print("="*60)
        print("1. Gerar Ranking de Episódios da Semana")
        print("2. Gerar Ranking de Animes Mais Esperados")
        print("3. Gerar Ambos os Rankings")
        print("4. Sair")
        print("="*60)

        choice = input("Escolha uma opção: ")

        if choice == '1':
            run_weekly_ranking()
        elif choice == '2':
            run_anticipated_ranking()
        elif choice == '3':
            run_weekly_ranking()
            run_anticipated_ranking()
        elif choice == '4':
            print("Saindo do sistema de rankings.")
            break
        else:
            print("Opção inválida. Por favor, escolha novamente.")

    print("\nProcesso concluído!")

if __name__ == "__main__":
    main()