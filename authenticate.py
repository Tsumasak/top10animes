import requests
import json
import secrets
import hashlib
import base64
import webbrowser
import traceback
from datetime import datetime

def generate_pkce_challenge():
    """Gera um code_verifier e code_challenge para o fluxo PKCE."""
    code_verifier = secrets.token_urlsafe(32)
    code_challenge = code_verifier # For MyAnimeList, code_challenge_method is 'plain'
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

        # Generate PKCE challenge and verifier
        code_verifier, code_challenge = generate_pkce_challenge()
        
        if not client_id:
            print("Client ID não encontrado em config.json. Por favor, adicione-o primeiro.")
            return

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

        try:
            auth_code = redirected_url.split('?code=')[1].split('&')[0]
        except IndexError:
            print("\nErro: Não consegui encontrar o 'code' na URL que você colou.")
            print(f"A URL deve ser algo como: {config['mal_api']['redirect_uri']}/?code=SEU_CODIGO_AQUI")
            return

        print("\nCódigo de autorização recebido. Trocando por um token de acesso...")

        token_url = "https://myanimelist.net/v1/oauth2/token"
        
        payload = {
            'client_id': client_id,
            'client_secret': config['mal_api']['client_secret'],
            'grant_type': 'authorization_code',
            'code': auth_code,
            'redirect_uri': config['mal_api']['redirect_uri'],
            'code_verifier': code_verifier # Use the local verifier
        }
        
        response = requests.post(token_url, data=payload)
        response.raise_for_status()
        
        token_data = response.json()
        
        config['mal_api']['access_token'] = token_data['access_token']
        config['mal_api']['refresh_token'] = token_data['refresh_token']
        config['mal_api']['token_expiry'] = token_data['expires_in']
        
        save_config(config)
        
        print("\n" + "="*80)
        print("|| SUCESSO! ||")
        print("="*80)
        print("\nTokens de acesso foram obtidos e salvos com sucesso em config.json!")

    except requests.exceptions.RequestException as e:
        print("\n--- ERRO DE CONEXÃO ---")
        print(f"Não consegui me conectar ao servidor do MyAnimeList para obter o token: {e}")
        if e.response is not None:
            print(f"Status Code: {e.response.status_code}")
            error_details = e.response.text
            print(f"Resposta do Servidor: {error_details}")
            with open('error_log.txt', 'a', encoding='utf-8') as f:
                f.write(f"{datetime.now()} - API AUTHENTICATION ERROR: {e.response.status_code} - {error_details}\n")
    except Exception as e:
        print(f"\n--- OCORREU UM ERRO INESPERADO ---")
        print(f"Erro: {e}")
        with open('error_log.txt', 'a', encoding='utf-8') as f:
            f.write(f"{datetime.now()} - UNEXPECTED AUTH ERROR: {str(e)}\n")
            traceback.print_exc(file=f)
    finally:
        input("\nPressione Enter para fechar o terminal...")

if __name__ == "__main__":
    main()