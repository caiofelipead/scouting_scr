import sys
sys.path.insert(0, '/workspaces/scouting_scr')

from sqlalchemy import create_engine, text

database_url = "postgresql://postgres:0kolSmQmLvltTspVHZkrLPsDJV5DryYL@interchange.proxy.rlwy.net:56826/railway?sslmode=require"

print("🔗 Testando conexão direta...\n")

try:
    engine = create_engine(database_url, echo=False)
    
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version()"))
        version = result.fetchone()[0]
        print(f"✅ CONEXÃO OK!")
        print(f"📊 PostgreSQL: {version[:50]}...\n")
        
        # Testar query
        result = conn.execute(text("SELECT COUNT(*) FROM jogadores"))
        total = result.fetchone()[0]
        print(f"✅ Total de jogadores: {total}")
        
except Exception as e:
    print(f"❌ ERRO: {e}")
    import traceback
    traceback.print_exc()
