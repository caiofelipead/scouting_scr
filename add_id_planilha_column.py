#!/usr/bin/env python3
from database import ScoutingDatabase
from sqlalchemy import text

print("🔧 Adicionando coluna id_planilha ao banco...")

db = ScoutingDatabase()

try:
    with db.engine.connect() as conn:
        # Adicionar coluna id_planilha (permite NULL por enquanto)
        conn.execute(text('''
            ALTER TABLE jogadores 
            ADD COLUMN IF NOT EXISTS id_planilha INTEGER
        '''))
        conn.commit()

        print("✅ Coluna id_planilha adicionada com sucesso!")

        # Verificar
        result = conn.execute(text('''
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'jogadores' 
            AND column_name = 'id_planilha'
        '''))

        if result.fetchone():
            print("✅ Coluna confirmada no banco!")
        else:
            print("⚠️  Coluna não encontrada após criação")

except Exception as e:
    print(f"❌ Erro: {e}")

print("\n📝 Próximo passo: Importar id_planilha do Google Sheets")
