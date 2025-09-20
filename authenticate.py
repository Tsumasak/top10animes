
import requests
import json
import secrets
import hashlib
import base64
import webbrowser

def generate_pkce_challenge():
    """Gera um code_verifier e code_challenge para o fluxo PKCE."""
    code_verifier = secrets.token_urlsafe(100)[:128]
    hashed = hashlib.sha256(code_verifier.encode('utf-8')).digest()
    code_challenge = base64.urlsafe_b64encode(hashed).decode('utf-8').replace('=', '')
    return code_verifier, code_challenge

def get_config():
    """Carrega a configuração do arquivo JSON."""
    with open('config.json', 'r') as f:
        return json.load(f)

def save_config(config_data):
    """Salva os dados de configuração no arquivo JSON."""
    with open('config.json', 'w') as f:
        json.dump(config_data, f, indent=2)

def main():
    """Função principal para o fluxo de autenticação."""
    try:
        config = get_config()
        client_id = config['mal_api']['client_id']
        
        if not client_id:
            print("Client ID não encontrado em config.json. Por favor, adicione-o primeiro.")
            return

        code_verifier, code_challenge = generate_pkce_challenge()
        
        auth_url = (
            f"https://myanimelist.net/v1/oauth2/authorize?"
            f"response_type=code&"
            f"client_id={client_id}&"
            f"code_challenge={code_challenge}&"
            f"redirect_uri={config['mal_api']['redirect_uri']}"
        )

        print("="*80)
        print("|| PASSO 1: AUTORIZAÇÃO ||")
        print("="*80)
        print("\nPor favor, abra a seguinte URL no seu navegador para autorizar a aplicação:")
        print(f"\nURL: {auth_url}\n")
        
        try:
            webbrowser.open(auth_url)
            print("Tentei abrir a URL no seu navegador padrão.")
        except Exception:
            print("Não consegui abrir o navegador automaticamente. Por favor, copie e cole a URL manualmente.")

        print("\nApós autorizar, o MyAnimeList irá te redirecionar para uma URL `localhost`.")
        redirected_url = input("Por favor, cole a URL completa para a qual você foi redirecionado: ")

        # Extrair o código de autorização da URL redirecionada
        try:
            auth_code = redirected_url.split('?code=')[1].split('&')[0]
        except IndexError:
            print("\nErro: Não consegui encontrar o 'code' na URL que você colou.")
            print("A URL deve ser algo como: http://localhost:8080/?code=SEU_CODIGO_AQUI")
            return

        print("\nCódigo de autorização recebido. Trocando por um token de acesso...")

        token_url = "https://myanimelist.net/v1/oauth2/token"
        payload = {
            'client_id': client_id,
            'client_secret': config['mal_api']['client_secret'],
            'grant_type': 'authorization_code',
            'code': auth_code,
            'redirect_uri': config['mal_api']['redirect_uri'],
            'code_verifier': code_verifier
        }
        
        response = requests.post(token_url, data=payload)
        response.raise_for_status()
        
        token_data = response.json()
        
        # Salvar os tokens no config.json
        config['mal_api']['access_token'] = token_data['access_token']
        config['mal_api']['refresh_token'] = token_data['refresh_token']
        config['mal_api']['token_expiry'] = token_data['expires_in']
        
        save_config(config)
        
        print("\n" + "="*80)
        print("|| SUCESSO! ||")
        print("="*80)
        print("\nTokens de acesso foram obtidos e salvos com sucesso em config.json!")
        print("Agora você pode usar a API do MyAnimeList.")

    except requests.exceptions.RequestException as e:
        print(f"\nErro de rede ao tentar obter o token: {e}")
        if e.response:
            print(f"Detalhes do erro: {e.response.text}")
    except Exception as e:
        print(f"\nOcorreu um erro inesperado: {e}")

if __name__ == "__main__":
    main()
