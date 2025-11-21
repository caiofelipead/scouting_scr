"""
Script de Correção - Adiciona nota_potencial ao banco existente
Execute antes de rodar o dashboard se tiver banco antigo
"""

import sqlite3
import os

def corrigir_banco():
    db_path = 'scouting.db'
    
    if not os.path.exists(db_path):
        print("✅ Banco não existe ainda - será criado corretamente na primeira execução")
        return True
    
    print("🔧 Verificando estrutura do banco...")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("PRAGMA table_info(avaliacoes)")
        colunas = [col[1] for col in cursor.fetchall()]
        
        if 'nota_potencial' in colunas:
            print("✅ Coluna nota_potencial já existe!")
            return True
        
        print("⚠️  Adicionando coluna nota_potencial...")
        cursor.execute("ALTER TABLE avaliacoes ADD COLUMN nota_potencial REAL CHECK(nota_potencial >= 1 AND nota_potencial <= 5)")
        conn.commit()
        print("✅ Banco corrigido com sucesso!")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

if __name__ == "__main__":
    corrigir_banco()
