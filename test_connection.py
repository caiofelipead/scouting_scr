import os
import sys
from dotenv import load_dotenv

# Adicionar raiz ao path
sys.path.insert(0, '/workspaces/scouting_scr')

load_dotenv()

print("=" * 60)
print("🧪 TESTE DE CONEXÃO - Railway PostgreSQL")
print("=" * 60)

database_url = os.getenv('DATABASE_URL')

if database_url:
    url_mascarada = database_url.replace(
        database_url.split('@')[0].split('//')[1],
        "postgres:****"
    )
    print(f"\n✅ DATABASE_URL encontrada!")
    print(f"📍 URL: {url_mascarada}\n")
else:
    print("\n❌ DATABASE_URL NÃO encontrada!\n")
    exit(1)

print("🔗 Tentando conectar ao banco...\n")

try:
    # ✅ Import do database.py da raiz
    from database import ScoutingDatabase
    
    db = ScoutingDatabase()
    print("✅ Conexão estabelecida com sucesso!\n")
    
    print("🔍 Testando query...\n")
    jogadores = db.get_jogadores_com_vinculos()
    
    print(f"✅ Query executada com sucesso!")
    print(f"📊 Total de jogadores: {len(jogadores)}\n")
    
    if len(jogadores) > 0:
        print(f"👤 Primeiro jogador: {jogadores.iloc[0]['nome']}")
    
    print("\n" + "=" * 60)
    print("🎉 TESTE CONCLUÍDO COM SUCESSO!")
    print("=" * 60)
    
except Exception as e:
    print(f"❌ ERRO: {e}\n")
    import traceback
    traceback.print_exc()
    print("\n" + "=" * 60)
