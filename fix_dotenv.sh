#!/bin/bash
# Adicionar load_dotenv ao database.py

echo "🔧 Adicionando suporte ao .env no database.py..."

# Backup
cp database.py database.py.bak2

# Adicionar import da dotenv após os outros imports
# Procurar a linha "import os" e adicionar logo depois
sed -i '/^import os$/a from dotenv import load_dotenv

# Carregar variáveis de ambiente do .env
load_dotenv()' database.py

echo "✅ load_dotenv() adicionado!"
echo ""
echo "📝 Verificando:"
grep -A 3 "^import os" database.py | head -6
