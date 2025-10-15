import os
from update_top_episodes import update_top_episodes_data
from update_anticipated_animes import update_anticipated_animes_data
from export_data import export_data # Assuming export_data.py has an export_data() function
from manual_episodes import ManualEpisodeManager

def display_menu():
    print("\n--- Menu de Atualização de Dados ---")
    print("1. Atualizar apenas Top Episodes")
    print("2. Atualizar apenas Most Anticipated")
    print("3. Atualizar Ambos")
    print("4. 🔧 Adicionar Episódios Manuais")
    print("5. Sair")
    print("------------------------------------")

def main_menu():
    while True:
        display_menu()
        choice = input("Escolha uma opção: ")

        if choice == '1':
            update_top_episodes_data()
            print("\nTop Episodes atualizado. Exportando dados para o frontend...")
            export_data()
            print("Exportação concluída.")
        elif choice == '2':
            update_anticipated_animes_data()
            print("\nMost Anticipated atualizado. Exportando dados para o frontend...")
            export_data()
            print("Exportação concluída.")
        elif choice == '3':
            update_top_episodes_data()
            update_anticipated_animes_data()
            print("\nAmbos atualizados. Exportando dados para o frontend...")
            export_data()
            print("Exportação concluída.")
        elif choice == '4':
            print("\n🔧 Iniciando Sistema de Episódios Manuais...")
            manual_manager = ManualEpisodeManager()
            manual_manager.run()
            print("\nVoltando ao menu principal...")
        elif choice == '5':
            print("Saindo...")
            break
        else:
            print("Opção inválida. Tente novamente.")

if __name__ == '__main__':
    main_menu()
