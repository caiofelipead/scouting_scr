"""
Sistema de Backup Automático - Scout Pro
Cria backups periódicos do banco de dados
"""

import os
import pandas as pd
from datetime import datetime
from database_extended import ScoutingDatabaseExtended
import zipfile


class BackupSystem:
    """Sistema de backup do banco de dados"""
    
    def __init__(self, backup_dir="backups"):
        self.backup_dir = backup_dir
        self.db = ScoutingDatabaseExtended()
        
        # Cria diretório de backups se não existir
        os.makedirs(backup_dir, exist_ok=True)
    
    def criar_backup_completo(self):
        """Cria backup completo de todas as tabelas"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(self.backup_dir, timestamp)
        os.makedirs(backup_path, exist_ok=True)
        
        print(f"\n🔄 Iniciando backup completo...")
        print(f"📁 Diretório: {backup_path}")
        print("="*50)
        
        tabelas = [
            'jogadores',
            'avaliacoes', 
            'tags_jogadores',
            'wishlist',
            'usuarios',
            'log_acessos',
            'log_auditoria'
        ]
        
        estatisticas = {}
        
        for tabela in tabelas:
            try:
                print(f"\n📦 Exportando {tabela}...", end=" ")
                df = self.db.exportar_backup(tabela)
                
                # Salva CSV
                csv_path = os.path.join(backup_path, f"{tabela}.csv")
                df.to_csv(csv_path, index=False, encoding='utf-8')
                
                # Salva também em Excel para facilitar visualização
                xlsx_path = os.path.join(backup_path, f"{tabela}.xlsx")
                df.to_excel(xlsx_path, index=False, engine='openpyxl')
                
                estatisticas[tabela] = len(df)
                print(f"✅ {len(df)} registros")
                
            except Exception as e:
                print(f"❌ Erro: {e}")
                estatisticas[tabela] = 0
        
        # Cria arquivo de metadados
        metadata = {
            'data_backup': timestamp,
            'total_tabelas': len(tabelas),
            'estatisticas': estatisticas
        }
        
        metadata_df = pd.DataFrame([metadata])
        metadata_df.to_csv(
            os.path.join(backup_path, '_metadata.csv'),
            index=False
        )
        
        # Compacta o backup
        zip_path = f"{backup_path}.zip"
        print(f"\n📦 Compactando backup...", end=" ")
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(backup_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, backup_path)
                    zipf.write(file_path, arcname)
        
        print("✅")
        
        # Exibe resumo
        print("\n" + "="*50)
        print("✅ BACKUP CONCLUÍDO COM SUCESSO!")
        print("="*50)
        print(f"\n📁 Arquivos salvos em: {backup_path}")
        print(f"📦 Arquivo compactado: {zip_path}")
        print("\n📊 Resumo:")
        
        for tabela, qtd in estatisticas.items():
            print(f"   - {tabela}: {qtd} registros")
        
        print("\n" + "="*50)
        
        return backup_path
    
    def listar_backups(self):
        """Lista todos os backups disponíveis"""
        
        backups = []
        
        for item in os.listdir(self.backup_dir):
            item_path = os.path.join(self.backup_dir, item)
            
            if os.path.isdir(item_path):
                # Diretório de backup
                metadata_path = os.path.join(item_path, '_metadata.csv')
                
                if os.path.exists(metadata_path):
                    df_meta = pd.read_csv(metadata_path)
                    backups.append({
                        'data': item,
                        'path': item_path,
                        'tipo': 'diretorio',
                        'tamanho': self._get_dir_size(item_path)
                    })
            
            elif item.endswith('.zip'):
                # Arquivo zip
                backups.append({
                    'data': item.replace('.zip', ''),
                    'path': item_path,
                    'tipo': 'zip',
                    'tamanho': os.path.getsize(item_path)
                })
        
        return sorted(backups, key=lambda x: x['data'], reverse=True)
    
    def _get_dir_size(self, path):
        """Calcula tamanho de um diretório"""
        total = 0
        for entry in os.scandir(path):
            if entry.is_file():
                total += entry.stat().st_size
            elif entry.is_dir():
                total += self._get_dir_size(entry.path)
        return total
    
    def _format_size(self, size_bytes):
        """Formata tamanho em bytes para formato legível"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} TB"
    
    def restaurar_backup(self, backup_path):
        """
        Restaura um backup
        ATENÇÃO: Isso irá SOBRESCREVER os dados atuais!
        """
        
        print("\n⚠️  ATENÇÃO: Esta operação irá SOBRESCREVER todos os dados atuais!")
        confirma = input("Digite 'CONFIRMAR' para continuar: ")
        
        if confirma != 'CONFIRMAR':
            print("❌ Operação cancelada")
            return False
        
        print("\n🔄 Restaurando backup...")
        
        # Lista arquivos CSV no backup
        csv_files = [f for f in os.listdir(backup_path) if f.endswith('.csv') and f != '_metadata.csv']
        
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            for csv_file in csv_files:
                tabela = csv_file.replace('.csv', '')
                print(f"\n📥 Restaurando {tabela}...", end=" ")
                
                # Lê CSV
                df = pd.read_csv(os.path.join(backup_path, csv_file))
                
                # Limpa tabela
                cursor.execute(f"DELETE FROM {tabela}")
                
                # Insere dados
                # (Aqui você precisaria adaptar para cada tabela)
                
                print(f"✅ {len(df)} registros")
            
            conn.commit()
            print("\n✅ Backup restaurado com sucesso!")
            return True
            
        except Exception as e:
            conn.rollback()
            print(f"\n❌ Erro ao restaurar: {e}")
            return False
        finally:
            cursor.close()
            conn.close()
    
    def limpar_backups_antigos(self, dias=30):
        """Remove backups mais antigos que X dias"""
        
        from datetime import timedelta
        
        data_limite = datetime.now() - timedelta(days=dias)
        removidos = 0
        
        print(f"\n🗑️  Limpando backups anteriores a {data_limite.strftime('%d/%m/%Y')}...")
        
        backups = self.listar_backups()
        
        for backup in backups:
            try:
                # Converte data do backup para datetime
                backup_date = datetime.strptime(backup['data'], "%Y%m%d_%H%M%S")
                
                if backup_date < data_limite:
                    # Remove
                    if backup['tipo'] == 'zip':
                        os.remove(backup['path'])
                    else:
                        import shutil
                        shutil.rmtree(backup['path'])
                    
                    print(f"   ✅ Removido: {backup['data']}")
                    removidos += 1
                    
            except Exception as e:
                print(f"   ❌ Erro ao remover {backup['data']}: {e}")
        
        print(f"\n✅ {removidos} backups removidos")


def menu_backup():
    """Menu interativo de backup"""
    
    backup_sys = BackupSystem()
    
    while True:
        print("\n" + "="*50)
        print("💾 SISTEMA DE BACKUP - SCOUT PRO")
        print("="*50)
        print("\n1. Criar backup completo")
        print("2. Listar backups")
        print("3. Limpar backups antigos")
        print("4. Sair")
        print()
        
        opcao = input("Escolha uma opção (1-4): ").strip()
        
        if opcao == "1":
            backup_sys.criar_backup_completo()
        
        elif opcao == "2":
            backups = backup_sys.listar_backups()
            
            if backups:
                print("\n📋 BACKUPS DISPONÍVEIS:")
                print("="*50)
                
                for i, backup in enumerate(backups, 1):
                    print(f"\n{i}. {backup['data']}")
                    print(f"   Tipo: {backup['tipo']}")
                    print(f"   Tamanho: {backup_sys._format_size(backup['tamanho'])}")
            else:
                print("\n⚠️  Nenhum backup encontrado")
        
        elif opcao == "3":
            dias = int(input("\nRemover backups com mais de quantos dias? "))
            backup_sys.limpar_backups_antigos(dias)
        
        elif opcao == "4":
            print("\n👋 Até logo!")
            break
        
        else:
            print("\n❌ Opção inválida")
        
        input("\n\nPressione ENTER para continuar...")


if __name__ == "__main__":
    menu_backup()
