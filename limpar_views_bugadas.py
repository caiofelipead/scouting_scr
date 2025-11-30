#!/usr/bin/env python3
"""
Script para remover views bugadas do PostgreSQL Railway
Resolve o erro: syntax error at or near "NOT" - IF NOT EXISTS
"""

from database import ScoutingDatabase
from sqlalchemy import text

def limpar_views():
    """Remove views antigas que estão causando erro"""
    
    print("🚀 Conectando ao banco de dados...")
    db = ScoutingDatabase()
    
    views_para_remover = [
        'vw_benchmark_posicoes',
        'vw_alertas_inteligentes'
    ]
    
    try:
        with db.engine.connect() as conn:
            print("\n🗑️ Removendo views antigas...")
            
            for view_name in views_para_remover:
                try:
                    sql = f"DROP VIEW IF EXISTS {view_name} CASCADE"
                    conn.execute(text(sql))
                    print(f"   ✅ {view_name} removida")
                except Exception as e:
                    print(f"   ⚠️ {view_name}: {e}")
            
            conn.commit()
            print("\n✅ Limpeza concluída com sucesso!")
            print("\n📝 Próximo passo: Reinicie o app no Streamlit Cloud")
            print("   O erro 'syntax error at or near NOT' deve desaparecer!")
            
    except Exception as e:
        print(f"\n❌ Erro ao conectar ao banco: {e}")
        return False
    
    finally:
        db.fechar_conexao()
    
    return True

if __name__ == "__main__":
    print("=" * 60)
    print("🔧 LIMPADOR DE VIEWS BUGADAS - Scout Pro")
    print("=" * 60)
    
    limpar_views()
