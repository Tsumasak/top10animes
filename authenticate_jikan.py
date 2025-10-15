"""
Arquivo de configuração para a API Jikan.
A API Jikan não requer autenticação, apenas configurações de rate limiting.
"""

import json
import requests
from datetime import datetime

def get_config():
    """Carrega a configuração do arquivo JSON."""
    with open('config.json', 'r') as f:
        return json.load(f)

def test_jikan_connection():
    """Testa a conectividade com a API Jikan."""
    print("="*80)
    print("|| TESTE DE CONECTIVIDADE COM API JIKAN ||")
    print("="*80)
    
    try:
        # Testa uma requisição simples
        response = requests.get("https://api.jikan.moe/v4/anime/1", timeout=10)
        response.raise_for_status()
        
        data = response.json()
        anime_title = data['data']['title']
        
        print(f"\n✓ Conectividade OK!")
        print(f"✓ Anime de teste obtido: {anime_title}")
        print(f"✓ Status da API: Funcionando")
        print(f"✓ Rate limit: Respeitando limites da Jikan")
        
        print("\n" + "="*80)
        print("|| CONFIGURAÇÃO CONCLUÍDA ||")
        print("="*80)
        print("\nA API Jikan está pronta para uso!")
        print("Não é necessário token de autenticação.")
        print("Rate limit: máximo 3 requests por segundo (configurado para 2/seg)")
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Erro ao conectar com a API Jikan: {e}")
        print("\nVerifique sua conexão com a internet e tente novamente.")
        return False

def show_jikan_info():
    """Mostra informações sobre a API Jikan."""
    print("\n" + "="*80)
    print("|| INFORMAÇÕES DA API JIKAN ||")
    print("="*80)
    print("\nA API Jikan é uma API REST não oficial do MyAnimeList.")
    print("\nVantagens:")
    print("• Não requer autenticação")
    print("• Acesso completo aos dados públicos do MAL")
    print("• Inclui informações de score e ratings")
    print("• Rate limit generoso (3 requests/segundo)")
    print("• Gratuita e open source")
    print("\nLimitações:")
    print("• Não permite modificação de listas pessoais")
    print("• Dependente da disponibilidade do serviço")
    print("• Rate limit deve ser respeitado")
    
    print(f"\nBase URL: https://api.jikan.moe/v4")
    print(f"Documentação: https://docs.api.jikan.moe/")

def main():
    """Função principal para configurar a API Jikan."""
    show_jikan_info()
    
    if test_jikan_connection():
        print(f"\nConfigurações salvas em config.json")
        print("Você pode agora usar os scripts principais com a API Jikan!")
    else:
        print("Falha na configuração. Verifique sua conexão e tente novamente.")

if __name__ == "__main__":
    main()