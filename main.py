import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import time
import json
from scraper_utils import debug_print, log_error, parse_members_count, parse_air_date
from html_generator import generate_html_page

def get_season_anime_urls(min_members=20000):
    # URLs para buscar animes
    urls = [
        "https://myanimelist.net/anime/season",
        "https://myanimelist.net/anime/season/2025/summer"
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0'
    }
    
    debug_print("Iniciando coleta de URLs de animes...")
    
    anime_list = []
    anime_urls_seen = set()  # Para evitar duplicatas
    
    for url in urls:
        debug_print(f"Buscando em: {url}", 2)
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
        except requests.RequestException as e:
            debug_print(f"Erro ao acessar {url}: {e}", 2)
            log_error(e)
            continue
        
        soup = BeautifulSoup(response.content, 'html.parser')
        seasonal_items = soup.find_all('div', class_='seasonal-anime')
        
        debug_print(f"Animes encontrados em {url}: {len(seasonal_items)}", 2)
        
        for item in seasonal_items:
            try:
                link_tag = item.find('a', class_='link-title')
                if not link_tag or not link_tag.has_attr('href'):
                    continue
                    
                anime_url = link_tag['href']
                
                # Evitar duplicatas
                if anime_url in anime_urls_seen:
                    continue
                anime_urls_seen.add(anime_url)
                
                anime_title = link_tag.text.strip()
                
                img_tag = item.find('img')
                anime_img = None
                if img_tag:
                    anime_img = img_tag.get('data-src') or img_tag.get('src')
                
                member_tag = item.find('div', class_='scormem-item member')
                members_count = parse_members_count(member_tag.text) if member_tag else 0
                
                if members_count >= min_members:
                    anime_list.append({
                        'title': anime_title,
                        'url': anime_url,
                        'image': anime_img,
                        'members': members_count
                    })
            except Exception as e_inner:
                debug_print(f"Erro ao processar anime: {e_inner}", 3)
                log_error(e_inner)
        
        # Pequeno delay entre requests
        time.sleep(1)
    
    debug_print(f"Total de animes únicos encontrados: {len(anime_urls_seen)}")
    debug_print(f"Total de animes filtrados com {min_members}+ membros: {len(anime_list)}")
    return anime_list

def get_episodes_info(anime_url):
    try:
        debug_print(f"Processando episódios para: {anime_url}")
        episodes_url = anime_url.replace('/episodes', '/episode')
        if not episodes_url.endswith('/episode'):
            episodes_url = f"{anime_url}/episode"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(episodes_url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        anime_title_elem = soup.find('h1', class_='title-name')
        anime_title = anime_title_elem.text.strip().replace(' Episodes', '') if anime_title_elem else "Unknown"
        episode_table = soup.find('table', class_='episode_list') or next((t for t in soup.find_all('table') if 'episode' in str(t).lower()), None)
        if not episode_table:
            return None
        rows = episode_table.find_all('tr', class_='episode-list-data')
        today = datetime.now().date()
        start_of_week = today - timedelta(days=today.weekday() + 7)
        end_of_week = start_of_week + timedelta(days=6)
        episodes = []
        for row in rows:
            try:
                airdate_td = row.find('td', class_='episode-aired')
                if not airdate_td:
                    continue
                airdate = parse_air_date(airdate_td.text.strip())
                if not airdate or not (start_of_week <= airdate <= end_of_week):
                    continue
                ep_num_td = row.find('td', class_='episode-number')
                ep_num = ep_num_td.text.strip() if ep_num_td else "Unknown"
                title_td = row.find('td', class_='episode-title')
                ep_title = title_td.find('a').text.strip() if title_td and title_td.find('a') else (title_td.text.strip() if title_td else "Unknown")
                score_td = row.find('td', class_='episode-poll')
                score = 0.0
                if score_td and 'scored' in score_td.get('class', []):
                    try:
                        score = float(score_td.get('data-raw', '0'))
                    except ValueError:
                        score = 0.0
                episodes.append({
                    'anime_title': anime_title,
                    'episode_number': ep_num,
                    'episode_title': ep_title,
                    'score': score,
                    'airdate': airdate
                })
            except Exception as e_inner:
                debug_print(f"Erro ao processar episódio: {e_inner}", 3)
                log_error(e_inner)
        return episodes
    except Exception as e:
        debug_print(f"Erro ao coletar episódios de {anime_url}: {e}", 2)
        log_error(e)
        return None

def save_data_to_json(episodes, filename='episodes_data.json'):
    """Salva os dados dos episódios em JSON para reuso"""
    data = {
        'generated_at': datetime.now().isoformat(),
        'episodes': episodes
    }
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)

def load_data_from_json(filename='episodes_data.json'):
    """Carrega dados dos episódios do JSON"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return None

def main():
    try:
        print("Iniciando coleta de dados do MyAnimeList...")
        print("=" * 50)
        
        anime_list = get_season_anime_urls()
        print(f"\nTotal de animes filtrados: {len(anime_list)}")
        if not anime_list:
            print("\nNenhum anime encontrado. O script não pode continuar.")
            return
        
        today = datetime.now().date()
        start_of_last_week = today - timedelta(days=today.weekday() + 7)
        end_of_last_week = start_of_last_week + timedelta(days=6)
        print(f"\nBuscando episódios entre {start_of_last_week} e {end_of_last_week}")
        print("=" * 50)
        
        all_episodes = []
        for i, anime in enumerate(anime_list):
            print(f"\nProcessando anime {i+1}/{len(anime_list)}: {anime['title']}")
            episodes = get_episodes_info(anime['url'])
            if episodes:
                for ep in episodes:
                    ep['image'] = anime['image']
                    ep['url'] = anime['url']
                all_episodes.extend(episodes)
            else:
                print(f"  Nenhum episódio encontrado na última semana")
            time.sleep(1)
        
        # Salvar dados brutos
        save_data_to_json(all_episodes)
        
        episodes_with_score = [ep for ep in all_episodes if ep['score'] > 0]
        episodes_with_score.sort(key=lambda x: x['score'], reverse=True)
        top_50_episodes = episodes_with_score[:50]
        
        # Gerar HTML
        html_content = generate_html_page(top_50_episodes, start_of_last_week, end_of_last_week)
        with open('top_anime_episodes.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"\nArquivo 'top_anime_episodes.html' gerado com sucesso!")
        print(f"Total de episódios ranqueados: {len(top_50_episodes)}")
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")
        log_error(e)

if __name__ == "__main__":
    main()
