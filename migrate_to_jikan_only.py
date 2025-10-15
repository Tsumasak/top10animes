"""
Script de migração para sistema 100% JIKAN API
Remove completamente a dependência de scraping
"""

import os
import shutil
from datetime import datetime

def backup_old_system():
    """Faz backup do sistema antigo."""
    print("💾 Fazendo backup do sistema atual...")
    
    backup_dir = f"backup_scraping_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.makedirs(backup_dir, exist_ok=True)
    
    files_to_backup = [
        'main.py',
        'scraper_utils.py'
    ]
    
    for file in files_to_backup:
        if os.path.exists(file):
            shutil.copy2(file, backup_dir)
            print(f"  ✅ {file} → {backup_dir}/")
    
    print(f"✅ Backup salvo em: {backup_dir}")
    return backup_dir

def update_requirements():
    """Atualiza o requirements.txt removendo BeautifulSoup."""
    print("📦 Atualizando requirements.txt...")
    
    new_requirements = """requests==2.31.0
# beautifulsoup4==4.12.2  # Removido - não mais necessário
# Dependências para sistema 100% JIKAN API:
# - requests (para comunicação com API)
# - json, datetime (built-in Python)
"""
    
    with open('requirements.txt', 'w') as f:
        f.write(new_requirements)
    
    print("✅ requirements.txt atualizado (BeautifulSoup removido)")

def migrate_to_jikan_only():
    """Realiza a migração completa para sistema JIKAN-only."""
    print("🚀 MIGRAÇÃO PARA SISTEMA 100% JIKAN API")
    print("=" * 80)
    
    try:
        # 1. Backup
        backup_dir = backup_old_system()
        
        # 2. Substituir main.py
        print("\n🔄 Substituindo arquivo principal...")
        
        if os.path.exists('main.py'):
            shutil.move('main.py', f'{backup_dir}/main_old.py')
        
        shutil.copy2('main_jikan_only.py', 'main.py')
        print("✅ main.py atualizado para versão 100% JIKAN")
        
        # 3. Atualizar requirements
        update_requirements()
        
        # 4. Criar arquivo de informações
        create_migration_info(backup_dir)
        
        print("\n" + "=" * 80)
        print("🎉 MIGRAÇÃO CONCLUÍDA COM SUCESSO!")
        print("=" * 80)
        print("✅ Sistema agora usa 100% JIKAN API")
        print("✅ Scraping removido completamente")
        print("✅ BeautifulSoup não mais necessário")
        print(f"✅ Backup salvo em: {backup_dir}")
        
        print("\n🚀 PRÓXIMOS PASSOS:")
        print("1. Execute: python main.py")
        print("2. Teste a conectividade: opção 5 no menu")
        print("3. Gere os rankings com as novas funcionalidades")
        
        print("\n💡 PRINCIPAIS MELHORIAS:")
        print("• Sem dependência de scraping HTML")
        print("• Mais rápido e estável")
        print("• Informações mais ricas (scores detalhados)")
        print("• Algoritmo avançado de expectativa")
        print("• Sistema de períodos flexível")
        print("• Rate limiting automático")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Erro durante migração: {e}")
        return False

def create_migration_info(backup_dir):
    """Cria arquivo com informações da migração."""
    info_content = f"""# MIGRAÇÃO PARA SISTEMA 100% JIKAN API
Data da migração: {datetime.now().strftime('%d/%m/%Y às %H:%M')}
Backup localizado em: {backup_dir}

## PRINCIPAIS MUDANÇAS:

### ✅ REMOVIDO:
- Scraping HTML com BeautifulSoup
- Dependência de parsing de páginas web
- Funcionalidade get_episodes_info() antiga
- scraper_utils.py (mantido no backup)

### ✅ ADICIONADO:
- Sistema 100% baseado em JIKAN API
- Algoritmo avançado de cálculo de expectativa
- Sistema flexível de períodos (semana atual, anterior, personalizado)
- Cálculo inteligente de scores de episódios
- Informações detalhadas de animes (gêneros, estúdios, estatísticas)
- Testes de conectividade automáticos

### ✅ MELHORADO:
- Velocidade de execução
- Estabilidade (sem dependência de HTML)
- Quantidade de informações obtidas
- Interface de usuário mais amigável
- Tratamento de erros

## ARQUIVOS PRINCIPAIS:
- main.py → Interface principal (100% JIKAN)
- update_anticipated_animes.py → Sistema avançado de animes esperados
- update_top_episodes.py → Sistema de episódios sem scraping
- jikan_api.py → Funções base da API

## COMO USAR:
1. python main.py
2. Escolher opção desejada no menu
3. Seguir instruções na tela

## REVERSÃO:
Para reverter, execute: python revert_to_mal.py
(Isso restaurará o sistema MAL original, não o sistema híbrido)

Aproveite o novo sistema! 🎉
"""
    
    with open(f'{backup_dir}/MIGRATION_INFO.md', 'w', encoding='utf-8') as f:
        f.write(info_content)
    
    with open('JIKAN_MIGRATION.md', 'w', encoding='utf-8') as f:
        f.write(info_content)
    
    print("📝 Arquivo de informações criado: JIKAN_MIGRATION.md")

def main():
    """Função principal de migração."""
    print("🔄 MIGRADOR PARA SISTEMA 100% JIKAN API")
    print("=" * 80)
    print("Este script irá:")
    print("• Fazer backup do sistema atual")
    print("• Substituir main.py por versão 100% JIKAN")
    print("• Remover dependências de scraping")
    print("• Atualizar requirements.txt")
    print("=" * 80)
    
    response = input("\n💭 Deseja continuar com a migração? (s/N): ").strip().lower()
    
    if response in ['s', 'sim', 'y', 'yes']:
        success = migrate_to_jikan_only()
        
        if success:
            print("\n🎊 Migração realizada com sucesso!")
            print("Execute 'python main.py' para começar a usar o novo sistema.")
        else:
            print("\n❌ Falha na migração. Verifique os erros acima.")
    else:
        print("\n🚫 Migração cancelada pelo usuário.")

if __name__ == "__main__":
    main()