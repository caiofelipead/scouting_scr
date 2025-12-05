import os
from sqlalchemy import create_engine, text

DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    print("❌ DATABASE_URL não encontrada!")
    exit(1)

engine = create_engine(DATABASE_URL)

print("🚀 Adicionando coluna nota_potencial...")

try:
    with engine.connect() as conn:
        conn.execute(text("""
            ALTER TABLE avaliacoes 
            ADD COLUMN IF NOT EXISTS nota_potencial DECIMAL(2,1) 
            CHECK (nota_potencial >= 1 AND nota_potencial <= 5)
        """))
        
        # Preencher com 3.0 os registros existentes
        conn.execute(text("""
            UPDATE avaliacoes 
            SET nota_potencial = 3.0 
            WHERE nota_potencial IS NULL
        """))
        
        conn.commit()
        print("✅ Coluna nota_potencial adicionada!")
        print("✅ Registros existentes atualizados com valor 3.0")
        
except Exception as e:
    print(f"❌ Erro: {e}")
