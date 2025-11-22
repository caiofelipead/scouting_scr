"""
Script de Correção Rápida - Adiciona nota_potencial à tabela existente
Execute este script para corrigir o erro sem perder dados
"""

import sqlite3
import os

def corrigir_banco():
    """Adiciona a coluna nota_potencial se ela não existir"""
    
    db_path = 'scouting.db'
    
    if not os.path.exists(db_path):
        print("❌ Banco de dados não encontrado!")
        print("   Execute primeiro: python import_data.py")
        return False
    
    print("\n🔧 Corrigindo estrutura do banco de dados...")
    print("="*60)
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar se a coluna já existe
        cursor.execute("PRAGMA table_info(avaliacoes)")
        colunas = [col[1] for col in cursor.fetchall()]
        
        if 'nota_potencial' in colunas:
            print("✅ Coluna 'nota_potencial' já existe!")
            print("   Estrutura do banco está correta.")
        else:
            print("⚠️  Coluna 'nota_potencial' não encontrada")
            print("   Adicionando coluna...")
            
            cursor.execute("""
                ALTER TABLE avaliacoes 
                ADD COLUMN nota_potencial REAL 
                CHECK(nota_potencial >= 1 AND nota_potencial <= 5)
            """)
            
            conn.commit()
            print("✅ Coluna 'nota_potencial' adicionada com sucesso!")
        
        # Verificar estrutura final
        cursor.execute("PRAGMA table_info(avaliacoes)")
        colunas_final = cursor.fetchall()
        
        print("\n📊 Estrutura atual da tabela avaliacoes:")
        print("-"*60)
        for col in colunas_final:
            print(f"  ✓ {col[1]:20s} {col[2]}")
        
        conn.close()
        
        print("\n" + "="*60)
        print("✅ CORREÇÃO CONCLUÍDA!")
        print("="*60)
        print("\n🎯 Próximo passo:")
        print("   Execute: streamlit run dashboard.py")
        print("\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Erro ao corrigir banco: {e}")
        print("\n💡 Solução alternativa:")
        print("   1. Faça backup de scouting.db")
        print("   2. Execute: python fix_avaliacoes.py")
        print("   3. Execute: python import_data.py")
        return False

if __name__ == "__main__":
    corrigir_banco()