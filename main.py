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

def get_episodes_info(anime_url):
    try:
        episodes_url = anime_url.rstrip('/') + '/episode'
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(episodes_url, headers=headers)
        if response.status_code == 404:
            debug_print(f"Página de episódios não encontrada (404): {episodes_url}", 2)
            return None
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        anime_title = soup.find('h1', class_='title-name').text.strip().replace(' Episodes', '')
        episode_table = soup.find('table', class_='episode_list')
        if not episode_table: return None
        rows = episode_table.find_all('tr', class_='episode-list-data')
        today = datetime.now().date()
        start_of_week = today - timedelta(days=today.weekday() + 7)
        end_of_week = start_of_week + timedelta(days=6)
        episodes = []
        for row in rows:
            airdate = parse_air_date(row.find('td', class_='episode-aired').text.strip())
            if not airdate or not (start_of_week <= airdate <= end_of_week): continue
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
        year, season = get_current_season()
        # 1. Usar a API para buscar a lista de animes da temporada
        anime_list = get_seasonal_animes(year, season)
        
        if not anime_list:
            debug_print("Nenhum anime encontrado via API para o ranking semanal.", 1)
            return
            
        today = datetime.now().date()
        start_of_last_week = today - timedelta(days=today.weekday() + 7)
        end_of_last_week = start_of_last_week + timedelta(days=6)
        debug_print(f"Período de referência: {start_of_last_week.strftime('%d/%m')} a {end_of_last_week.strftime('%d/%m')}", 1)
        all_episodes = []
        
        # 2. Usar o scraper para buscar os scores de cada anime
        for i, anime in enumerate(anime_list):
            title_for_print = anime['title'].encode('cp1252', 'replace').decode('cp1252')
            debug_print(f"Processando anime {i+1}/{len(anime_list)}: {title_for_print}", 1)
            
            # Chamada ao scraper mantida para buscar scores
            episodes = get_episodes_info(anime['url']) 
            
            if episodes:
                for ep in episodes:
                    ep['image'] = anime['image']
                    ep['url'] = anime['url']
                all_episodes.extend(episodes)
                debug_print(f"Encontrados {len(episodes)} episódios para '{title_for_print}' na semana.", 2)
            time.sleep(1) # Manter a pausa para não sobrecarregar o servidor com o scraping
        
        if not all_episodes:
            print("Nenhum episódio encontrado na semana de referência.")
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
    run_weekly_ranking()
    run_anticipated_ranking()
    print("\nProcesso concluído! Ambas as páginas foram geradas.")

if __name__ == "__main__":
    main()
