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



def get_season_from_date(d):
    """Determina o ano e a estação a partir de uma data específica."""

    year = d.year
    # Define the start dates for each season for the given year
    fall_start = datetime(year, 9, 22).date()
    summer_start = datetime(year, 6, 21).date()
    spring_start = datetime(year, 3, 20).date()
    winter_start = datetime(year, 12, 21).date()

    if d >= fall_start and d < winter_start:
        return year, "fall"
    elif d >= summer_start and d < fall_start:
        return year, "summer"
    elif d >= spring_start and d < summer_start:
        return year, "spring"
    else: # Covers winter, including the wrap-around from December to the next year's March
        # If the date is in the early part of the year (before spring_start)
        if d < spring_start:
            return year -1, "winter" # It's the winter season that started last year
        else: # It must be in the late part of the year (after winter_start)
            return year, "winter"

def get_episodes_info(anime_url, start_date, end_date, api_anime_title):
    try:
        episodes_url = anime_url.rstrip('/') + '/episode'
        debug_print(f"Acessando pßgina de episdios: {episodes_url}", 3)
        headers = {'User-Agent': 'Mozilla/5.0'}
        
        # Primeira requisição para encontrar a última página
        response = requests.get(episodes_url, headers=headers)
        if response.status_code == 404:
            debug_print(f"Pßgina de episdios nÒo encontrada (404): {episodes_url}", 2)
            return None
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        # Lógica para encontrar e ir para a última página de episódios
        pagination_div = soup.find('div', class_='pagination')
        if pagination_div:
            last_page_link = pagination_div.find_all('a')[-1] # Pega o último link da paginação
            if last_page_link and 'href' in last_page_link.attrs:
                last_page_url = last_page_link['href']
                debug_print(f"Paginação encontrada. Acessando última página: {last_page_url}", 2)
                response = requests.get(last_page_url, headers=headers)
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

def save_data_to_json(episodes, filename='episodes_data.json', start_date=None, end_date=None):
    """Salva os dados dos episódios em JSON para reuso"""
    data = {
        'generated_at': datetime.now().isoformat(),
        'start_date': start_date,
        'end_date': end_date,
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

        # 1. Buscar animes da temporada atual e da anterior para incluir animes contínuos
        current_year, current_season = get_season_from_date(start_of_week)
        
        seasons_to_check = [(current_year, current_season)]
        if current_season == "winter":
            seasons_to_check.append((current_year - 1, "fall"))
        elif current_season == "spring":
            seasons_to_check.append((current_year, "winter"))
        elif current_season == "summer":
            seasons_to_check.append((current_year, "spring"))
        else: # fall
            seasons_to_check.append((current_year, "summer"))

        all_animes = []
        for year, season in seasons_to_check:
            all_animes.extend(get_seasonal_animes(year, season, limit=500, min_members=20000))

        # Remover duplicatas (animes que podem aparecer em ambas as listas)
        anime_list = list({anime['url']: anime for anime in all_animes}.values())
        
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
        
        save_data_to_json(top_50_episodes, filename='episodes_data.json', start_date=start_of_week, end_date=end_of_week)
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