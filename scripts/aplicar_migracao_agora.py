#!/usr/bin/env python3
"""
Script Simples de Migração FotMob
Usa a conexão existente do ScoutingDatabase
"""

import sys
from pathlib import Path

# Adiciona o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database import ScoutingDatabase
from sqlalchemy import text

def aplicar_migracao():
    """Aplica migração usando conexão existente"""

    print("🔵 Conectando ao banco de dados...")

    try:
        db = ScoutingDatabase()

        print("✅ Conectado ao banco de dados!\n")

        # Lê o arquivo SQL
        sql_file = Path(__file__).parent.parent / 'sql' / 'criar_tabela_fotmob.sql'

        if not sql_file.exists():
            print(f"❌ Arquivo SQL não encontrado: {sql_file}")
            return False

        print(f"📄 Lendo SQL: {sql_file.name}")

        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()

        # Divide o SQL em statements
        statements = [s.strip() for s in sql_content.split(';') if s.strip() and not s.strip().startswith('--')]

        print(f"📊 Executando {len(statements)} statements SQL...\n")

        with db.engine.begin() as conn:
            sucesso = 0
            erros = 0

            for i, statement in enumerate(statements, 1):
                try:
                    # Detecta tipo
                    statement_lower = statement.lower().strip()

                    if 'create table' in statement_lower:
                        tipo = "TABELA"
                        nome = statement_lower.split('create table if not exists')[1].split('(')[0].strip() if 'if not exists' in statement_lower else "?"
                    elif 'create index' in statement_lower:
                        tipo = "ÍNDICE"
                        nome = statement_lower.split('create index if not exists')[1].split('on')[0].strip() if 'if not exists' in statement_lower else "?"
                    elif 'create or replace view' in statement_lower:
                        tipo = "VIEW"
                        nome = statement_lower.split('create or replace view')[1].split('as')[0].strip()
                    elif 'comment on' in statement_lower:
                        tipo = "COMENTÁRIO"
                        nome = ""
                    else:
                        tipo = "STATEMENT"
                        nome = ""

                    print(f"[{i}/{len(statements)}] {tipo} {nome}...", end=" ")

                    conn.execute(text(statement))

                    print("✅")
                    sucesso += 1

                except Exception as e:
                    print(f"❌ {e}")
                    erros += 1

        print(f"\n{'='*60}")
        print(f"🎉 Migração Concluída!")
        print(f"{'='*60}")
        print(f"✅ Sucesso: {sucesso}")
        print(f"❌ Erros:   {erros}")

        if erros == 0:
            print("\n✨ Tabela estatisticas_fotmob criada com sucesso!")
            print("✨ Views vw_perfil_completo_jogador e vw_ranking_combinado criadas!")
            print("\n🚀 Sistema pronto para usar as novas visualizações!")

        return erros == 0

    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("""
╔═══════════════════════════════════════════════╗
║   APLICANDO MIGRAÇÃO FOTMOB                  ║
╚═══════════════════════════════════════════════╝
    """)

    sucesso = aplicar_migracao()

    sys.exit(0 if sucesso else 1)
