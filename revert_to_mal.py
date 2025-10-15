"""
Script de reversão para voltar à API MAL original.
Execute este script se quiser reverter as mudanças.
"""

import shutil
import os

def restore_backup():
    """Restaura os arquivos do backup."""
    print("="*80)
    print("|| REVERSÃO PARA API MAL ORIGINAL ||")
    print("="*80)
    
    if not os.path.exists('backup'):
        print("❌ Pasta de backup não encontrada!")
        print("Não é possível reverter as alterações.")
        return False
    
    try:
        # Lista os arquivos a serem restaurados
        backup_files = [
            'mal_api.py',
            'main.py',
            'authenticate.py',
            'scraper_utils.py',
            'config.json.backup',
            'requirements.txt.backup'
        ]
        
        print("Restaurando arquivos do backup...")
        
        # Restaura arquivos Python
        for filename in ['mal_api.py', 'main.py', 'authenticate.py', 'scraper_utils.py']:
            backup_path = os.path.join('backup', filename)
            if os.path.exists(backup_path):
                shutil.copy2(backup_path, filename)
                print(f"✓ {filename} restaurado")
        
        # Restaura configuração
        if os.path.exists('backup/config.json.backup'):
            shutil.copy2('backup/config.json.backup', 'config.json')
            print("✓ config.json restaurado")
        
        # Restaura requirements
        if os.path.exists('backup/requirements.txt.backup'):
            shutil.copy2('backup/requirements.txt.backup', 'requirements.txt')
            print("✓ requirements.txt restaurado")
        
        print("\n" + "="*80)
        print("|| REVERSÃO CONCLUÍDA ||")
        print("="*80)
        print("✓ Arquivos originais restaurados com sucesso!")
        print("✓ Sistema voltou para API MAL original")
        print("\nLembre-se de:")
        print("1. Executar authenticate.py para reconfigurar tokens")
        print("2. Verificar se as credenciais MAL ainda são válidas")
        print("3. Testar as funcionalidades antes de usar em produção")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro durante a reversão: {e}")
        return False

def backup_jikan_files():
    """Faz backup dos arquivos Jikan antes da reversão."""
    print("Fazendo backup dos arquivos Jikan...")
    
    jikan_backup_dir = 'backup_jikan'
    if not os.path.exists(jikan_backup_dir):
        os.makedirs(jikan_backup_dir)
    
    jikan_files = [
        'jikan_api.py',
        'authenticate_jikan.py',
        'test_migration.py'
    ]
    
    for filename in jikan_files:
        if os.path.exists(filename):
            shutil.copy2(filename, os.path.join(jikan_backup_dir, filename))
            print(f"✓ {filename} salvo em backup_jikan/")

def main():
    """Função principal de reversão."""
    print("AVISO: Esta operação irá reverter todas as alterações para a API Jikan")
    print("e restaurar o sistema original com API MAL.")
    
    response = input("\nDeseja continuar com a reversão? (s/N): ").strip().lower()
    
    if response in ['s', 'sim', 'y', 'yes']:
        backup_jikan_files()
        
        if restore_backup():
            print("\nReversão concluída com sucesso!")
            print("Arquivos Jikan salvos em 'backup_jikan/' para referência futura")
        else:
            print("\nFalha na reversão. Verifique os arquivos manualmente.")
    else:
        print("Reversão cancelada.")

if __name__ == "__main__":
    main()