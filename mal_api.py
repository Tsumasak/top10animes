
import requests
import json
from datetime import datetime, timedelta

def get_config():
    """Carrega a configuração do arquivo JSON."""
    with open('config.json', 'r') as f:
        return json.load(f)

def save_config(config_data):
    """Salva os dados de configuração no arquivo JSON."""
    with open('config.json', 'w') as f:
        json.dump(config_data, f, indent=2)

def refresh_access_token():
    """Atualiza o token de acesso usando o refresh token."""
    print("Token de acesso expirado. Tentando atualizar...")
    config = get_config()
    mal_api_config = config.get('mal_api', {})
    
    client_id = mal_api_config.get('client_id')
    client_secret = mal_api_config.get('client_secret')
    refresh_token = mal_api_config.get('refresh_token')

    if not all([client_id, client_secret, refresh_token]):
        raise Exception("Faltam client_id, client_secret ou refresh_token no config.json")

    token_url = "https://myanimelist.net/v1/oauth2/token"
    payload = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
        'client_id': client_id,
        'client_secret': client_secret
    }
    
    try:
        response = requests.post(token_url, data=payload)
        response.raise_for_status()
        
        token_data = response.json()
        
        # Atualiza a configuração com os novos tokens
        config['mal_api']['access_token'] = token_data['access_token']
        config['mal_api']['refresh_token'] = token_data['refresh_token']
        config['mal_api']['token_expiry'] = (datetime.now() + timedelta(seconds=token_data['expires_in'])).isoformat()
        
        save_config(config)
        print("Token de acesso atualizado com sucesso.")
        return token_data['access_token']
        
    except requests.exceptions.RequestException as e:
        print(f"Erro ao tentar atualizar o token: {e}")
        if e.response:
            print(f"Detalhes do erro: {e.response.text}")
        raise

def make_api_request(url, params={}):
    """Faz uma requisição à API do MAL, lidando com a autenticação e atualização de token."""
    config = get_config()
    access_token = config.get('mal_api', {}).get('access_token')

    if not access_token:
        raise Exception("Token de acesso não encontrado. Execute o script authenticate.py primeiro.")

    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        
        # Se o token expirou (401), tenta atualizar e refazer a requisição
        if response.status_code == 401:
            new_access_token = refresh_access_token()
            headers['Authorization'] = f'Bearer {new_access_token}'
            response = requests.get(url, headers=headers, params=params)
        
        response.raise_for_status()
        return response.json()
        
    except requests.exceptions.RequestException as e:
        print(f"Erro na requisição à API para {url}: {e}")
        if e.response:
            print(f"Detalhes do erro: {e.response.text}")
        return None

def get_best_anime_picture(anime_id):
    """Busca a melhor imagem para um anime específico via API."""
    #debug_print(f"Buscando imagem de alta resolução para o anime ID: {anime_id}", 3)
    url = f"https://api.myanimelist.net/v2/anime/{anime_id}"
    params = {'fields': 'pictures'}
    data = make_api_request(url, params)
    if data and data.get('pictures'):
        return data['pictures'][0].get('large')
    elif data and data.get('main_picture'):
        return data['main_picture'].get('large')
    return None

def get_anticipated_animes(limit=50):
    """
    Busca os animes mais esperados (ranking 'upcoming') da API do MAL.
    """
    print("Buscando ranking de animes mais esperados via API...")
    url = "https://api.myanimelist.net/v2/anime/ranking"
    params = {
        'ranking_type': 'upcoming',
        'limit': limit,
        'fields': 'id,title,main_picture,num_list_users,alternative_titles'
    }
    
    data = make_api_request(url, params)
    
    if not data or 'data' not in data:
        print("Não foi possível obter os dados dos animes mais esperados.")
        return []
        
    # Formata os dados para o formato esperado pelo frontend
    formatted_animes = []
    for item in data['data']:
        node = item['node']
        
        # Busca imagem de alta resolução (mais lento)
        best_image = get_best_anime_picture(node['id'])
        time.sleep(0.5) # Pausa para não sobrecarregar a API

        # Prioriza o título em inglês
        english_title = node.get('alternative_titles', {}).get('en', '')
        title = english_title if english_title else node['title']

        formatted_animes.append({
            'ranking': item['ranking']['rank'],
            'title': title,
            'url': f"https://myanimelist.net/anime/{node['id']}",
            'image': best_image or (node['main_picture'].get('large', node['main_picture'].get('medium')) if 'main_picture' in node else None),
            'members_count': node.get('num_list_users', 0),
            'members_display': f"{node.get('num_list_users', 0):,}"
        })
        
    print(f"Encontrados {len(formatted_animes)} animes no ranking de mais esperados.")
    return formatted_animes

def get_seasonal_animes(year, season, limit=100, min_members=20000):
    """
    Busca animes de uma temporada específica, lidando com paginação.
    """
    print(f"Buscando animes da temporada {season.capitalize()} {year} via API...")
    url = f"https://api.myanimelist.net/v2/anime/season/{year}/{season}"
    params = {
        'limit': limit,
        'fields': 'id,title,main_picture,num_list_users,alternative_titles',
        'sort': 'anime_num_list_users'
    }
    
    all_animes_from_season = []
    while url:
        data = make_api_request(url, params)
        if not data or 'data' not in data:
            break
        
        all_animes_from_season.extend(data['data'])
        
        # Pega a URL da próxima página, se existir
        url = data.get('paging', {}).get('next')
        params = {} # A URL da próxima página já contém os parâmetros

    # Formata e filtra os dados
    formatted_animes = []
    for anime in all_animes_from_season:
        node = anime['node']
        members_count = node.get('num_list_users', 0)
        if members_count >= min_members:
            # Busca imagem de alta resolução (mais lento)
            best_image = get_best_anime_picture(node['id'])
            time.sleep(0.5) # Pausa para não sobrecarregar a API

            # Prioriza o título em inglês
            english_title = node.get('alternative_titles', {}).get('en', '')
            title = english_title if english_title else node['title']

            formatted_animes.append({
                'title': title,
                'url': f"https://myanimelist.net/anime/{node['id']}",
                'image': best_image or (node['main_picture'].get('large', node['main_picture'].get('medium')) if 'main_picture' in node else None),
                'members': members_count
            })
            
    print(f"Total de animes filtrados para o ranking semanal: {len(formatted_animes)}")
    return formatted_animes

