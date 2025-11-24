#!/usr/bin/env python3
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

print("🔍 Testando Conexão Railway PostgreSQL")
print("="*70)

DATABASE_URL = os.getenv('DATABASE_URL')

if not DATABASE_URL:
    print("❌ DATABASE_URL não encontrada no .env")
    exit(1)

print(f"✅ DATABASE_URL carregada")
print(f"   Host: {DATABASE_URL.split('@')[1].split(':')[0] if '@' in DATABASE_URL else 'N/A'}")

# Testar conexão
try:
    from sqlalchemy import create_engine, text

    # Nota: Railway usa domínio interno, precisa ajustar para externo
    # postgres.railway.internal → será substituído automaticamente

    print("\n🔌 Conectando ao PostgreSQL...")
    engine = create_engine(DATABASE_URL)

    with engine.connect() as conn:
        result = conn.execute(text("SELECT version()"))
        version = result.fetchone()[0]
        print(f"✅ Conectado com sucesso!")
        print(f"   {version.split(',')[0]}")

        # Verificar tabelas
        result = conn.execute(text(
            "SELECT table_name FROM information_schema.tables "
            "WHERE table_schema = 'public'"
        ))
        tables = [row[0] for row in result.fetchall()]

        if tables:
            print(f"\n📊 Tabelas existentes: {', '.join(tables)}")
        else:
            print("\n⚠️  Nenhuma tabela encontrada (banco vazio)")

except Exception as e:
    print(f"❌ Erro ao conectar: {e}")
    print("\n💡 Dica: Se o erro for 'could not translate host name',")
    print("   o domínio 'postgres.railway.internal' só funciona dentro do Railway.")
    print("   Use o domínio público em vez disso.")

print("\n" + "="*70)
