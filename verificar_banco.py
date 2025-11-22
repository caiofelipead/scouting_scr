1"""
Script de Verificação do Banco de Dados
Verifica integridade e mostra estatísticas
"""

import sqlite3
import pandas as pd
from datetime import datetime
import os

def verificar_banco():
    """Verifica estado do banco de dados"""
    
    print("\n" + "="*60)
    print("🔍 VERIFICAÇÃO DO BANCO DE DADOS")
    print("="*60)
    
    # Verificar se arquivo existe
    if not os.path.exists('scouting.db'):
        print("\n❌ Arquivo scouting.db NÃO ENCONTRADO!")
        print("\n💡 Execute: python import_data.py")
        return False
    
    # Informações do arquivo
    tamanho = os.path.getsize('scouting.db') / 1024
    modificado = datetime.fromtimestamp(os.path.getmtime('scouting.db'))
    
    print(f"\n📁 Arquivo: scouting.db")
    print(f"📊 Tamanho: {tamanho:.2f} KB")
    print(f"🕐 Última modificação: {modificado.strftime('%d/%m/%Y %H:%M:%S')}")
    
    # Conectar ao banco
    try:
        conn = sqlite3.connect('scouting.db')
        cursor = conn.cursor()
        
        # Verificar tabelas
        print("\n" + "="*60)
        print("📊 TABELAS DO BANCO")
        print("="*60)
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tabelas = cursor.fetchall()
        
        for tabela in tabelas:
            nome_tabela = tabela[0]
            cursor.execute(f"SELECT COUNT(*) FROM {nome_tabela}")
            total = cursor.fetchone()[0]
            print(f"✅ {nome_tabela}: {total} registro(s)")
        
        # Estatísticas de Avaliações
        print("\n" + "="*60)
        print("📝 ESTATÍSTICAS DE AVALIAÇÕES")
        print("="*60)
        
        try:
            # Total de avaliações
            cursor.execute("SELECT COUNT(*) FROM avaliacoes")
            total_aval = cursor.fetchone()[0]
            print(f"\n✅ Total de avaliações: {total_aval}")
            
            if total_aval > 0:
                # Jogadores com avaliações
                cursor.execute("""
                SELECT COUNT(DISTINCT id_jogador) 
                FROM avaliacoes
                """)
                jogadores_avaliados = cursor.fetchone()[0]
                print(f"✅ Jogadores avaliados: {jogadores_avaliados}")
                
                # Última avaliação
                cursor.execute("""
                SELECT MAX(data_avaliacao), MAX(created_at)
                FROM avaliacoes
                """)
                ultima_data, ultima_criacao = cursor.fetchone()
                print(f"✅ Última avaliação: {ultima_data}")
                
                # Média de avaliações por jogador
                media = total_aval / jogadores_avaliados
                print(f"✅ Média de avaliações por jogador: {media:.1f}")
                
                # Listar últimas 5 avaliações
                print("\n📋 Últimas 5 Avaliações:")
                print("-"*60)
                
                query = """
                SELECT 
                    a.id_avaliacao,
                    j.nome,
                    a.data_avaliacao,
                    a.nota_potencial,
                    a.avaliador
                FROM avaliacoes a
                JOIN jogadores j ON a.id_jogador = j.id_jogador
                ORDER BY a.created_at DESC
                LIMIT 5
                """
                
                df = pd.read_sql_query(query, conn)
                
                for _, row in df.iterrows():
                    print(f"\n#{row['id_avaliacao']} - {row['nome']}")
                    print(f"   Data: {row['data_avaliacao']}")
                    print(f"   Potencial: {row['nota_potencial']:.1f}")
                    print(f"   Avaliador: {row['avaliador'] if row['avaliador'] else 'Não informado'}")
        
        except Exception as e:
            print(f"\n⚠️  Erro ao buscar avaliações: {str(e)}")
            print("   Tabela de avaliações pode estar vazia ou corrompida")
        
        # Verificar integridade
        print("\n" + "="*60)
        print("🔧 VERIFICAÇÃO DE INTEGRIDADE")
        print("="*60)
        
        cursor.execute("PRAGMA integrity_check")
        resultado = cursor.fetchone()
        
        if resultado[0] == 'ok':
            print("\n✅ Banco de dados íntegro!")
        else:
            print(f"\n⚠️  Problemas encontrados: {resultado[0]}")
        
        conn.close()
        
        print("\n" + "="*60)
        print("✅ VERIFICAÇÃO CONCLUÍDA")
        print("="*60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Erro ao verificar banco: {str(e)}")
        return False

def exportar_avaliacoes_csv():
    """Exporta todas as avaliações para CSV"""
    
    if not os.path.exists('scouting.db'):
        print("❌ Banco de dados não encontrado!")
        return False
    
    try:
        conn = sqlite3.connect('scouting.db')
        
        query = """
        SELECT 
            a.id_avaliacao,
            j.id_jogador,
            j.nome as nome_jogador,
            v.posicao,
            v.clube,
            a.data_avaliacao,
            a.nota_potencial,
            a.nota_tatico,
            a.nota_tecnico,
            a.nota_fisico,
            a.nota_mental,
            a.observacoes,
            a.avaliador,
            a.created_at
        FROM avaliacoes a
        JOIN jogadores j ON a.id_jogador = j.id_jogador
        LEFT JOIN vinculos v ON j.id_jogador = v.id_jogador
        ORDER BY a.created_at DESC
        """
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        if len(df) == 0:
            print("\n⚠️  Nenhuma avaliação para exportar")
            return False
        
        # Criar pasta de exports
        os.makedirs('exports', exist_ok=True)
        
        # Nome do arquivo
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        arquivo = f'exports/avaliacoes_export_{timestamp}.csv'
        
        # Exportar
        df.to_csv(arquivo, index=False, encoding='utf-8-sig')
        
        print("\n" + "="*60)
        print("✅ EXPORTAÇÃO CONCLUÍDA")
        print("="*60)
        print(f"📁 Arquivo: {arquivo}")
        print(f"📊 Total de avaliações: {len(df)}")
        print("="*60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Erro ao exportar: {str(e)}")
        return False

def menu():
    """Menu interativo"""
    
    while True:
        print("\n" + "="*60)
        print("🔍 VERIFICAÇÃO DO BANCO DE DADOS")
        print("="*60)
        print("\n1 - Verificar estado do banco")
        print("2 - Exportar avaliações para CSV")
        print("3 - Verificação rápida")
        print("0 - Sair")
        print("="*60)
        
        opcao = input("\nEscolha uma opção: ").strip()
        
        if opcao == "1":
            verificar_banco()
        
        elif opcao == "2":
            exportar_avaliacoes_csv()
        
        elif opcao == "3":
            # Verificação rápida
            if os.path.exists('scouting.db'):
                conn = sqlite3.connect('scouting.db')
                cursor = conn.cursor()
                
                cursor.execute("SELECT COUNT(*) FROM avaliacoes")
                total = cursor.fetchone()[0]
                
                conn.close()
                
                print(f"\n✅ Banco encontrado!")
                print(f"📝 Total de avaliações: {total}")
            else:
                print("\n❌ Banco não encontrado!")
        
        elif opcao == "0":
            print("\n👋 Até logo!")
            break
        
        else:
            print("\n❌ Opção inválida!")
        
        if opcao in ["1", "2", "3"]:
            input("\nPressione ENTER para continuar...")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == 'quick':
            # Verificação rápida via CLI
            conn = sqlite3.connect('scouting.db')
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM avaliacoes")
            total = cursor.fetchone()[0]
            conn.close()
            print(f"Avaliações no banco: {total}")
    else:
        menu()
