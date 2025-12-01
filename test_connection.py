import os
from dotenv import load_dotenv

# Carregar .env
load_dotenv()

print("=" * 60)
print("🧪 TESTE DE CONEXÃO - Railway PostgreSQL")
print("=" * 60)

# Verificar se .env foi carregado
database_url = os.getenv('DATABASE_URL')

if database_url:
    # Mascarar senha para não expor
    url_mascarada = database_url.replace(
        database_url.split('@')[0].split('//')[1],
        "postgres:****"
    )
    print(f"\n✅ DATABASE_URL encontrada!")
    print(f"📍 URL: {url_mascarada}\n")
else:
    print("\n❌ DATABASE_URL NÃO encontrada!")
    print("💡 Verifique se o arquivo .env existe na raiz do projeto\n")
    exit(1)

# Tentar conectar
print("🔗 Tentando conectar ao banco...\n")

try:
    from app.database import ScoutingDatabase
    
    db = ScoutingDatabase()
    
    print("✅ Conexão estabelecida com sucesso!\n")
    
    # Testar query
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
    print("💡 Possíveis causas:")
    print("   1. Arquivo .env não está na raiz do projeto")
    print("   2. DATABASE_URL está incorreta")
    print("   3. Firewall bloqueando conexão")
    print("   4. Banco Railway está offline")
    print("\n" + "=" * 60)
