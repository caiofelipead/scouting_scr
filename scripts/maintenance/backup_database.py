"""
Script de Backup do Banco de Dados
Cria cópias de segurança do scouting.db
"""

import os
import shutil
import sqlite3
from datetime import datetime


def fazer_backup():
    """Cria backup do banco de dados"""

    # Verificar se o banco existe
    if not os.path.exists("scouting.db"):
        print("❌ Banco de dados não encontrado!")
        return False

    # Criar pasta de backups
    os.makedirs("backups", exist_ok=True)

    # Nome do arquivo de backup com timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"backups/scouting_backup_{timestamp}.db"

    try:
        # Fazer backup usando SQLite
        conn_origem = sqlite3.connect("scouting.db")
        conn_backup = sqlite3.connect(backup_file)

        conn_origem.backup(conn_backup)

        conn_backup.close()
        conn_origem.close()

        # Informações sobre o backup
        tamanho = os.path.getsize(backup_file) / 1024  # KB

        print("\n" + "=" * 60)
        print("✅ BACKUP REALIZADO COM SUCESSO!")
        print("=" * 60)
        print(f"📁 Arquivo: {backup_file}")
        print(f"📊 Tamanho: {tamanho:.2f} KB")
        print(f"🕐 Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        print("=" * 60)

        # Listar estatísticas do banco
        conn = sqlite3.connect("scouting.db")
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT COUNT(*) FROM jogadores")
            total_jogadores = cursor.fetchone()[0]
            print(f"\n📊 Estatísticas do Backup:")
            print(f"   • Jogadores: {total_jogadores}")

            cursor.execute("SELECT COUNT(*) FROM avaliacoes")
            total_avaliacoes = cursor.fetchone()[0]
            print(f"   • Avaliações: {total_avaliacoes}")

            cursor.execute("SELECT COUNT(*) FROM vinculos")
            total_vinculos = cursor.fetchone()[0]
            print(f"   • Vínculos: {total_vinculos}")

            cursor.execute("SELECT COUNT(*) FROM alertas")
            total_alertas = cursor.fetchone()[0]
            print(f"   • Alertas: {total_alertas}")
        except:
            pass

        conn.close()

        # Limpar backups antigos (manter apenas os últimos 10)
        limpar_backups_antigos()

        return True

    except Exception as e:
        print(f"\n❌ Erro ao fazer backup: {str(e)}")
        return False


def limpar_backups_antigos(manter=10):
    """Remove backups antigos, mantendo apenas os N mais recentes"""

    if not os.path.exists("backups"):
        return

    # Listar todos os backups
    backups = [f for f in os.listdir("backups") if f.endswith(".db")]
    backups.sort(reverse=True)  # Mais recentes primeiro

    # Remover os mais antigos
    if len(backups) > manter:
        removidos = 0
        for backup in backups[manter:]:
            try:
                os.remove(f"backups/{backup}")
                removidos += 1
            except:
                pass

        if removidos > 0:
            print(f"\n🗑️  {removidos} backup(s) antigo(s) removido(s)")


def listar_backups():
    """Lista todos os backups disponíveis"""

    if not os.path.exists("backups"):
        print("\n📁 Nenhum backup encontrado")
        return

    backups = [f for f in os.listdir("backups") if f.endswith(".db")]

    if not backups:
        print("\n📁 Nenhum backup encontrado")
        return

    backups.sort(reverse=True)

    print("\n" + "=" * 60)
    print("📁 BACKUPS DISPONÍVEIS")
    print("=" * 60)

    for i, backup in enumerate(backups, 1):
        caminho = f"backups/{backup}"
        tamanho = os.path.getsize(caminho) / 1024

        # Extrair data do nome do arquivo
        try:
            timestamp = backup.replace("scouting_backup_", "").replace(".db", "")
            data = datetime.strptime(timestamp, "%Y%m%d_%H%M%S")
            data_formatada = data.strftime("%d/%m/%Y %H:%M:%S")
        except:
            data_formatada = "Data desconhecida"

        print(f"\n{i}. {backup}")
        print(f"   📅 {data_formatada}")
        print(f"   📊 {tamanho:.2f} KB")

    print("=" * 60)


def restaurar_backup(arquivo_backup):
    """Restaura um backup"""

    if not os.path.exists(arquivo_backup):
        print(f"❌ Backup não encontrado: {arquivo_backup}")
        return False

    print("\n⚠️  ATENÇÃO: Isso vai SUBSTITUIR o banco de dados atual!")
    resposta = input("Deseja continuar? (sim/não): ")

    if resposta.lower() not in ["sim", "s", "yes", "y"]:
        print("❌ Restauração cancelada")
        return False

    try:
        # Fazer backup do atual antes de restaurar
        if os.path.exists("scouting.db"):
            backup_atual = (
                f'backups/antes_restaurar_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db'
            )
            shutil.copy2("scouting.db", backup_atual)
            print(f"✅ Backup do banco atual salvo em: {backup_atual}")

        # Restaurar
        shutil.copy2(arquivo_backup, "scouting.db")

        print("\n" + "=" * 60)
        print("✅ BACKUP RESTAURADO COM SUCESSO!")
        print("=" * 60)
        print(f"📁 Arquivo restaurado: {arquivo_backup}")
        print("=" * 60)

        return True

    except Exception as e:
        print(f"\n❌ Erro ao restaurar backup: {str(e)}")
        return False


def menu():
    """Menu interativo"""

    while True:
        print("\n" + "=" * 60)
        print("💾 SISTEMA DE BACKUP - SCOUT PRO")
        print("=" * 60)
        print("\n1 - Fazer backup agora")
        print("2 - Listar backups disponíveis")
        print("3 - Restaurar backup")
        print("4 - Backup automático antes de atualizar código")
        print("0 - Sair")
        print("=" * 60)

        opcao = input("\nEscolha uma opção: ").strip()

        if opcao == "1":
            fazer_backup()

        elif opcao == "2":
            listar_backups()

        elif opcao == "3":
            listar_backups()
            arquivo = input(
                "\nDigite o nome completo do arquivo (ex: scouting_backup_20250121_143022.db): "
            ).strip()
            if arquivo:
                restaurar_backup(f"backups/{arquivo}")

        elif opcao == "4":
            print("\n💡 Execute este comando ANTES de atualizar o código:")
            print("   python backup_database.py")
            print("\n   Isso criará um backup automático!")
            fazer_backup()

        elif opcao == "0":
            print("\n👋 Até logo!")
            break

        else:
            print("\n❌ Opção inválida!")

        if opcao in ["1", "2", "3", "4"]:
            input("\nPressione ENTER para continuar...")


if __name__ == "__main__":
    # Se executado sem argumentos, mostra menu
    import sys

    if len(sys.argv) > 1:
        if sys.argv[1] == "auto":
            fazer_backup()
    else:
        menu()
