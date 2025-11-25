"""
migrate_financeiro.py
Script de migração para adicionar colunas financeiras à tabela jogadores
Execute uma vez para atualizar a estrutura do banco
"""

from database import ScoutingDatabase
from sqlalchemy import text


def migrar_colunas_financeiras():
    """Adiciona colunas financeiras à tabela jogadores"""
    
    db = ScoutingDatabase()
    
    # Colunas a adicionar
    colunas = [
        ("salario_mensal_min", "DECIMAL(12,2)"),
        ("salario_mensal_max", "DECIMAL(12,2)"),
        ("moeda_salario", "VARCHAR(10) DEFAULT 'BRL'"),
        ("bonificacoes", "TEXT"),
        ("custo_transferencia", "DECIMAL(12,2)"),
        ("clausula_rescisoria", "DECIMAL(12,2)"),
        ("percentual_direitos_economicos", "INTEGER DEFAULT 100"),
        ("condicoes_negocio", "TEXT"),
        ("observacoes_financeiras", "TEXT"),
        ("agente_nome", "VARCHAR(255)"),
        ("agente_empresa", "VARCHAR(255)"),
        ("agente_telefone", "VARCHAR(50)"),
        ("agente_email", "VARCHAR(255)"),
        ("agente_comissao", "DECIMAL(5,2)"),
    ]
    
    print("🔄 Iniciando migração de colunas financeiras...")
    
    with db.engine.connect() as conn:
        for coluna, tipo in colunas:
            try:
                # Verifica se a coluna já existe
                if db.db_type == 'postgresql':
                    check_query = """
                        SELECT column_name 
                        FROM information_schema.columns 
                        WHERE table_name = 'jogadores' AND column_name = :coluna
                    """
                else:
                    check_query = f"PRAGMA table_info(jogadores)"
                
                if db.db_type == 'postgresql':
                    result = conn.execute(text(check_query), {'coluna': coluna})
                    existe = result.fetchone() is not None
                else:
                    result = conn.execute(text(check_query))
                    colunas_existentes = [row[1] for row in result.fetchall()]
                    existe = coluna in colunas_existentes
                
                if not existe:
                    alter_query = f"ALTER TABLE jogadores ADD COLUMN {coluna} {tipo}"
                    conn.execute(text(alter_query))
                    print(f"  ✅ Coluna '{coluna}' adicionada")
                else:
                    print(f"  ⏭️ Coluna '{coluna}' já existe")
                    
            except Exception as e:
                print(f"  ⚠️ Erro na coluna '{coluna}': {e}")
        
        conn.commit()
    
    print("\n✅ Migração concluída!")
    db.fechar_conexao()


if __name__ == "__main__":
    migrar_colunas_financeiras()
