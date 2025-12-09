#!/usr/bin/env python3
"""
Script de Migração: Adicionar Tabela FotMob e Views
====================================================
Cria a tabela estatisticas_fotmob e views de análise combinada

Uso:
  python scripts/migrar_fotmob.py

Autor: Scout Pro
Data: 2025-12-09
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.pool import NullPool

# Adiciona o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

load_dotenv()


def executar_migracao():
    """Executa migração do banco de dados"""

    database_url = os.getenv('DATABASE_URL')

    if not database_url:
        print("❌ Erro: DATABASE_URL não encontrado no .env")
        print("💡 Este script precisa rodar conectado ao PostgreSQL do Railway")
        return False

    # Fix para Railway: postgres:// → postgresql://
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)

    print("🔵 Conectando ao PostgreSQL (Railway)...")

    try:
        engine = create_engine(
            database_url,
            poolclass=NullPool,
            connect_args={
                "connect_timeout": 10,
                "options": "-c timezone=utc"
            },
            pool_pre_ping=True
        )

        print("✅ Conectado ao PostgreSQL!\n")

        # Lê o arquivo SQL
        sql_file = Path(__file__).parent.parent / 'sql' / 'criar_tabela_fotmob.sql'

        if not sql_file.exists():
            print(f"❌ Arquivo SQL não encontrado: {sql_file}")
            return False

        print(f"📄 Lendo SQL: {sql_file.name}")

        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()

        # Divide o SQL em statements individuais (separados por ponto e vírgula)
        statements = [s.strip() for s in sql_content.split(';') if s.strip()]

        print(f"📊 Executando {len(statements)} statements SQL...\n")

        with engine.begin() as conn:
            sucesso = 0
            erros = 0

            for i, statement in enumerate(statements, 1):
                # Pula comentários
                if statement.startswith('--'):
                    continue

                try:
                    # Detecta tipo de statement
                    statement_lower = statement.lower().strip()

                    if statement_lower.startswith('create table'):
                        tipo = "TABELA"
                        # Extrai nome da tabela
                        nome = statement_lower.split('create table if not exists')[1].split('(')[0].strip()
                    elif statement_lower.startswith('create index'):
                        tipo = "ÍNDICE"
                        nome = statement_lower.split('create index if not exists')[1].split('on')[0].strip()
                    elif statement_lower.startswith('create or replace view'):
                        tipo = "VIEW"
                        nome = statement_lower.split('create or replace view')[1].split('as')[0].strip()
                    elif statement_lower.startswith('comment on'):
                        tipo = "COMENTÁRIO"
                        nome = ""
                    else:
                        tipo = "STATEMENT"
                        nome = ""

                    print(f"[{i}/{len(statements)}] Executando {tipo} {nome}...", end=" ")

                    conn.execute(text(statement))

                    print("✅")
                    sucesso += 1

                except Exception as e:
                    print(f"❌ Erro: {e}")
                    erros += 1

        print(f"\n{'='*60}")
        print(f"🎉 Migração Concluída!")
        print(f"{'='*60}")
        print(f"✅ Sucesso: {sucesso} statements")
        print(f"❌ Erros:   {erros} statements")

        if erros == 0:
            print("\n✨ Todas as operações foram executadas com sucesso!")
            print("\n📊 Objetos criados:")
            print("   - Tabela: estatisticas_fotmob")
            print("   - 4 Índices de performance")
            print("   - View: vw_perfil_completo_jogador")
            print("   - View: vw_ranking_combinado")
            print("\n🚀 Seu sistema agora está pronto para:")
            print("   1. Armazenar estatísticas do FotMob")
            print("   2. Combinar avaliações Scout Pro + FotMob")
            print("   3. Gerar rankings híbridos")
        else:
            print(f"\n⚠️  {erros} erro(s) encontrado(s). Verifique os detalhes acima.")

        return erros == 0

    except Exception as e:
        print(f"❌ Erro Crítico: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("""
╔═══════════════════════════════════════════════════════════╗
║   MIGRAÇÃO SCOUT PRO - INTEGRAÇÃO FOTMOB                 ║
║   Adiciona tabela de estatísticas e views avançadas      ║
╚═══════════════════════════════════════════════════════════╝
    """)

    sucesso = executar_migracao()

    if sucesso:
        print("\n✅ Migração executada com sucesso!")
        sys.exit(0)
    else:
        print("\n❌ Migração falhou. Corrija os erros e tente novamente.")
        sys.exit(1)
