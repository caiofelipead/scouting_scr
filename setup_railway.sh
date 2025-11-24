#!/bin/bash
# Configurar Railway PostgreSQL

echo "🚂 Configurando Railway PostgreSQL..."

# Criar arquivo .env com a DATABASE_URL
cat > .env << 'EOF'
# Railway PostgreSQL
DATABASE_URL=postgresql://postgres:OkolSmQmLvltTspVHZkrLPsDJVSDryYL@postgres.railway.internal:5432/railway

# Google Sheets
GOOGLE_SHEET_URL=https://docs.google.com/spreadsheets/d/1jNAxJIRoZxYH1jKwPCBrd4Na1ko04EDAYaUCVGsJdIA
EOF

echo "✅ Arquivo .env criado!"

# Adicionar .env ao .gitignore se não estiver
if ! grep -q "^.env$" .gitignore 2>/dev/null; then
    echo ".env" >> .gitignore
    echo "✅ .env adicionado ao .gitignore"
fi

echo ""
echo "📋 Próximos passos:"
echo "   1. Instalar psycopg2: pip install psycopg2-binary"
echo "   2. Testar conexão: python test_railway.py"
echo "   3. Migrar dados: python migrate_to_postgresql.py"
