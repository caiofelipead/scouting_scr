"""
Script para RECRIAR a tabela de avaliações com estrutura correta
Execute este script para corrigir o banco de dados
"""

import sqlite3
import os

def recriar_tabela_avaliacoes():
    """Recria a tabela de avaliações com a estrutura correta"""
    
    db_path = 'scouting.db'
    
    if not os.path.exists(db_path):
        print("❌ Banco de dados 'scouting.db' não encontrado!")
        print("   Execute primeiro: python import_data.py")
        return False
    
    print("\n" + "="*60)
    print("🔧 RECRIANDO TABELA DE AVALIAÇÕES")
    print("="*60)
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 1. Verificar se a tabela existe e qual sua estrutura
        print("\n📊 Verificando estrutura atual...")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='avaliacoes'")
        tabela_existe = cursor.fetchone()
        
        if tabela_existe:
            cursor.execute("PRAGMA table_info(avaliacoes)")
            colunas_antigas = cursor.fetchall()
            print(f"   ✓ Tabela encontrada com {len(colunas_antigas)} colunas:")
            for col in colunas_antigas:
                print(f"     - {col[1]} ({col[2]})")
            
            # 2. Fazer backup dos dados existentes
            print("\n💾 Fazendo backup de dados existentes...")
            cursor.execute("SELECT * FROM avaliacoes")
            dados_backup = cursor.fetchall()
            print(f"   ✓ {len(dados_backup)} avaliações encontradas")
        else:
            print("   ℹ️ Tabela 'avaliacoes' não existe ainda")
            dados_backup = []
        
        # 3. Dropar a tabela antiga
        print("\n🗑️  Removendo tabela antiga...")
        cursor.execute("DROP TABLE IF EXISTS avaliacoes")
        conn.commit()
        print("   ✓ Tabela removida")
        
        # 4. Criar tabela com estrutura CORRETA
        print("\n🏗️  Criando tabela com estrutura correta...")
        cursor.execute("""
        CREATE TABLE avaliacoes (
            id_avaliacao INTEGER PRIMARY KEY AUTOINCREMENT,
            id_jogador INTEGER NOT NULL,
            data_avaliacao DATE NOT NULL,
            nota_potencial REAL CHECK(nota_potencial >= 1 AND nota_potencial <= 5),
            nota_tatico REAL CHECK(nota_tatico >= 1 AND nota_tatico <= 5),
            nota_tecnico REAL CHECK(nota_tecnico >= 1 AND nota_tecnico <= 5),
            nota_fisico REAL CHECK(nota_fisico >= 1 AND nota_fisico <= 5),
            nota_mental REAL CHECK(nota_mental >= 1 AND nota_mental <= 5),
            observacoes TEXT,
            avaliador TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (id_jogador) REFERENCES jogadores(id_jogador)
        )
        """)
        conn.commit()
        print("   ✓ Tabela criada com sucesso!")
        
        # 5. Verificar estrutura nova
        print("\n✅ Verificando estrutura final...")
        cursor.execute("PRAGMA table_info(avaliacoes)")
        colunas_novas = cursor.fetchall()
        print(f"   ✓ Tabela criada com {len(colunas_novas)} colunas:")
        for col in colunas_novas:
            print(f"     ✓ {col[1]:20s} {col[2]}")
        
        # 6. Restaurar dados (se houver e se a estrutura antiga era compatível)
        if dados_backup:
            print(f"\n⚠️  Encontradas {len(dados_backup)} avaliações antigas.")
            print("   NOTA: Dados antigos NÃO serão restaurados automaticamente")
            print("   porque a estrutura mudou significativamente.")
            print("   Você precisará criar novas avaliações.")
        
        conn.close()
        
        print("\n" + "="*60)
        print("✅ TABELA RECRIADA COM SUCESSO!")
        print("="*60)
        print("\n🎯 Próximos passos:")
        print("   1. Execute: streamlit run dashboard.py")
        print("   2. Crie uma nova avaliação de teste")
        print("   3. Verifique se tudo funciona!")
        print("\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Erro ao recriar tabela: {e}")
        print("\n💡 Solução alternativa:")
        print("   1. Faça backup do arquivo scouting.db")
        print("   2. Delete o arquivo scouting.db")
        print("   3. Execute: python import_data.py")
        print("   4. Execute: streamlit run dashboard.py")
        return False

if __name__ == "__main__":
    recriar_tabela_avaliacoes()
