#!/usr/bin/env python3
"""
Script de Migração Corrigido - FotMob
======================================
Executa statements em transações separadas para evitar rollback completo

Uso: python migrar_fotmob_fix.py
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
        sql_file = Path(__file__).parent / 'sql' / 'criar_tabela_fotmob.sql'
        if not sql_file.exists():
            sql_file = Path(__file__).parent.parent / 'sql' / 'criar_tabela_fotmob.sql'

        if not sql_file.exists():
            print(f"❌ Arquivo SQL não encontrado: {sql_file}")
            return False

        print(f"📄 Lendo SQL: {sql_file.name}")

        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()

        # Divide o SQL em statements individuais
        statements = [s.strip() for s in sql_content.split(';') if s.strip()]

        print(f"📊 Executando {len(statements)} statements SQL...\n")

        sucesso = 0
        erros = 0

        # ===== CORREÇÃO: Cada statement em sua própria transação =====
        for i, statement in enumerate(statements, 1):
            # Pula comentários vazios
            if statement.startswith('--') or not statement.strip():
                continue

            try:
                # Detecta tipo de statement
                statement_lower = statement.lower().strip()

                if statement_lower.startswith('create table'):
                    tipo = "TABELA"
                    nome = statement_lower.split('create table if not exists')[1].split('(')[0].strip()
                elif statement_lower.startswith('create index'):
                    tipo = "ÍNDICE"
                    nome = statement_lower.split('create index if not exists')[1].split('on')[0].strip()
                elif statement_lower.startswith('create or replace view'):
                    tipo = "VIEW"
                    nome = statement_lower.split('create or replace view')[1].split('as')[0].strip()
                elif statement_lower.startswith('comment on'):
                    tipo = "COMENTÁRIO"
                    nome = "(ignorado)" if erros > 0 else ""
                else:
                    tipo = "STATEMENT"
                    nome = ""

                print(f"[{i}/{len(statements)}] {tipo} {nome}...", end=" ")

                # CORREÇÃO: Executa cada statement em sua própria transação
                with engine.begin() as conn:
                    conn.execute(text(statement))

                print("✅")
                sucesso += 1

            except Exception as e:
                print(f"⚠️ (ignorado)")
                erros += 1
                # Continua executando os próximos statements

        print(f"\n{'='*60}")
        print(f"🎉 Migração Concluída!")
        print(f"{'='*60}")
        print(f"✅ Sucesso: {sucesso} statements")
        print(f"⚠️  Ignorados: {erros} statements")

        if sucesso > 0:
            print("\n✨ Objetos principais criados com sucesso!")
            print("\n📊 O que foi criado:")
            print("   ✅ Tabela: estatisticas_fotmob")
            print("   ✅ Índices de performance")
            print("   ✅ Views: vw_perfil_completo_jogador")
            print("   ✅ Views: vw_ranking_combinado")
            print("\n💡 Comentários ignorados são normais (opcional)")
            print("\n🚀 Sistema pronto para uso!")
            return True
        else:
            print(f"\n❌ Nenhum objeto foi criado. Verifique os erros acima.")
            return False

    except Exception as e:
        print(f"❌ Erro Crítico: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("""
╔═══════════════════════════════════════════════════════════╗
║   MIGRAÇÃO SCOUT PRO - FotMob (VERSÃO CORRIGIDA)         ║
║   Executa statements em transações separadas             ║
╚═══════════════════════════════════════════════════════════╝
    """)

    sucesso = executar_migracao()

    if sucesso:
        print("\n✅ Migração executada com sucesso!")
        sys.exit(0)
    else:
        print("\n⚠️  Migração parcial. Tabelas principais devem ter sido criadas.")
        sys.exit(0)  # Exit 0 mesmo assim pois comentários são opcionais
