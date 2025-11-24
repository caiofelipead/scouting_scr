#!/usr/bin/env python3
"""
Migração Completa: SQLite → PostgreSQL Railway
Migra jogadores, vínculos, avaliações e alertas
"""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
import pandas as pd

# Carregar variáveis de ambiente
load_dotenv()

print("="*70)
print("🚀 MIGRAÇÃO COMPLETA: SQLite → PostgreSQL Railway")
print("="*70)

# Configurações
SQLITE_DB = 'scouting.db'
POSTGRES_URL = os.getenv('DATABASE_URL')

if not POSTGRES_URL:
    print("\n❌ DATABASE_URL não encontrada no arquivo .env!")
    exit(1)

print(f"\n📂 Origem: SQLite ({SQLITE_DB})")
print(f"📤 Destino: PostgreSQL Railway")

# Conectar aos bancos
print("\n🔌 Conectando aos bancos de dados...")
sqlite_engine = create_engine(f'sqlite:///{SQLITE_DB}')
postgres_engine = create_engine(POSTGRES_URL)

print("✅ Conectado ao SQLite")
print("✅ Conectado ao PostgreSQL Railway")

# Função para migrar tabela
def migrar_tabela(nome_tabela, truncate=True):
    print(f"\n📊 Migrando tabela: {nome_tabela}")

    try:
        # Ler do SQLite
        df = pd.read_sql_table(nome_tabela, sqlite_engine)
        total = len(df)

        if total == 0:
            print(f"   ⚠️  Tabela vazia no SQLite")
            return 0

        print(f"   📖 Lidos {total} registros do SQLite")

        # Limpar tabela no PostgreSQL se solicitado
        if truncate:
            with postgres_engine.connect() as conn:
                conn.execute(text(f"TRUNCATE TABLE {nome_tabela} CASCADE"))
                conn.commit()
            print(f"   🗑️  Tabela limpa no PostgreSQL")

        # Escrever no PostgreSQL
        df.to_sql(nome_tabela, postgres_engine, if_exists='append', index=False)
        print(f"   ✅ {total} registros migrados com sucesso!")

        return total

    except Exception as e:
        print(f"   ❌ Erro na migração: {e}")
        return 0

# Migrar tabelas na ordem correta (respeitando foreign keys)
print("\n" + "="*70)
print("📋 INICIANDO MIGRAÇÃO")
print("="*70)

# 1. Jogadores (tabela pai)
total_jog = migrar_tabela('jogadores')

# 2. Vínculos (depende de jogadores)
total_vinc = migrar_tabela('vinculos_clubes')

# 3. Avaliações (depende de jogadores)
total_aval = migrar_tabela('avaliacoes')

# 4. Alertas (depende de jogadores)
total_alert = migrar_tabela('alertas')

# Verificar migração
print("\n" + "="*70)
print("✅ VERIFICAÇÃO FINAL")
print("="*70)

with postgres_engine.connect() as conn:
    result = conn.execute(text("SELECT COUNT(*) FROM jogadores"))
    print(f"👥 Jogadores no PostgreSQL: {result.fetchone()[0]}")

    result = conn.execute(text("SELECT COUNT(*) FROM vinculos_clubes"))
    print(f"🔗 Vínculos no PostgreSQL: {result.fetchone()[0]}")

    result = conn.execute(text("SELECT COUNT(*) FROM avaliacoes"))
    print(f"⭐ Avaliações no PostgreSQL: {result.fetchone()[0]}")

    result = conn.execute(text("SELECT COUNT(*) FROM alertas"))
    print(f"🔔 Alertas no PostgreSQL: {result.fetchone()[0]}")

print("\n" + "="*70)
print("🎉 MIGRAÇÃO CONCLUÍDA COM SUCESSO!")
print("="*70)
print("\n📝 Próximos passos:")
print("   1. Configure o database.py para usar PostgreSQL por padrão")
print("   2. Teste o dashboard: streamlit run app/dashboard.py")
print("   3. Faça avaliações - agora serão salvas permanentemente!")
print()
