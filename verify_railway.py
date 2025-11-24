#!/usr/bin/env python3
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
import pandas as pd

load_dotenv()

print("📊 VERIFICAÇÃO DE DADOS - RAILWAY POSTGRESQL")
print("="*70)

DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)

with engine.connect() as conn:
    # Contar jogadores
    result = conn.execute(text("SELECT COUNT(*) FROM jogadores"))
    count_jog = result.fetchone()[0]
    print(f"\n👥 Jogadores: {count_jog}")

    # Contar vínculos
    result = conn.execute(text("SELECT COUNT(*) FROM vinculos_clubes"))
    count_vinc = result.fetchone()[0]
    print(f"🔗 Vínculos: {count_vinc}")

    # Contar avaliações
    result = conn.execute(text("SELECT COUNT(*) FROM avaliacoes"))
    count_aval = result.fetchone()[0]
    print(f"⭐ Avaliações: {count_aval}")

    # Contar alertas
    result = conn.execute(text("SELECT COUNT(*) FROM alertas"))
    count_alert = result.fetchone()[0]
    print(f"🔔 Alertas: {count_alert}")

    if count_jog > 0:
        print(f"\n📋 Amostra de Jogadores:")
        df = pd.read_sql_query(
            "SELECT nome, nacionalidade, altura, pe_dominante FROM jogadores LIMIT 5",
            conn
        )
        print(df.to_string(index=False))

        # Verificar pé dominante
        result = conn.execute(text(
            "SELECT pe_dominante, COUNT(*) as total FROM jogadores "
            "WHERE pe_dominante IS NOT NULL GROUP BY pe_dominante"
        ))
        print(f"\n🦶 Distribuição Pé Dominante:")
        for row in result:
            print(f"   {row[0]}: {row[1]}")

    if count_aval > 0:
        print(f"\n⭐ Últimas Avaliações:")
        df_aval = pd.read_sql_query(
            "SELECT a.nota_final, j.nome, a.data_avaliacao "
            "FROM avaliacoes a "
            "JOIN jogadores j ON a.id_jogador = j.id_jogador "
            "ORDER BY a.data_avaliacao DESC LIMIT 5",
            conn
        )
        print(df_aval.to_string(index=False))

print("\n" + "="*70)
