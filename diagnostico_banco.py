#!/usr/bin/env python3
import os
import sys

print("🔍 DIAGNÓSTICO DO BANCO DE DADOS")
print("="*70)

# Verificar variáveis de ambiente
print("\n📋 Variáveis de Ambiente:")
railway_vars = {k: v for k, v in os.environ.items() if 'RAILWAY' in k or 'DATABASE' in k or 'POSTGRES' in k}
if railway_vars:
    for k, v in railway_vars.items():
        # Ocultar senhas
        if 'PASSWORD' in k or 'SECRET' in k:
            print(f"  {k}: ****")
        else:
            print(f"  {k}: {v}")
else:
    print("  ⚠️  Nenhuma variável do Railway encontrada")

# Verificar tipo de banco em uso
print("\n🗄️  Tipo de Banco em Uso:")
try:
    from database import ScoutingDatabase
    db = ScoutingDatabase()

    # Verificar engine
    engine_type = str(db.engine.url).split(':')[0]
    print(f"  Engine: {engine_type}")
    print(f"  URL: {str(db.engine.url).split('@')[0]}@****")

    if 'sqlite' in engine_type:
        print("  ✅ Usando SQLite (Local)")
    elif 'postgres' in engine_type:
        print("  ✅ Usando PostgreSQL (Railway)")

        # Testar conexão
        try:
            with db.engine.connect() as conn:
                result = conn.execute(db.text("SELECT version()"))
                version = result.fetchone()[0]
                print(f"  ✅ Conectado: {version.split(',')[0]}")
        except Exception as e:
            print(f"  ❌ Erro de conexão: {e}")

    # Contar registros
    print("\n📊 Dados no Banco:")
    df = db.buscar_todos_jogadores()
    print(f"  Jogadores: {len(df)}")

    # Verificar avaliações
    try:
        conn = db.connect()
        import pandas as pd
        count_aval = pd.read_sql_query("SELECT COUNT(*) as n FROM avaliacoes", conn)
        print(f"  Avaliações: {count_aval['n'].iloc[0]}")
    except Exception as e:
        print(f"  Avaliações: Erro ao contar - {e}")

except Exception as e:
    print(f"  ❌ Erro ao conectar: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*70)
