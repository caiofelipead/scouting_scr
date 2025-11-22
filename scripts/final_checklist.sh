#!/bin/bash
# Nome do arquivo: scripts/final_checklist.sh

echo "📋 CHECKLIST FINAL - Scout Pro"
echo "="*60

# 1. Validar setup
echo "1️⃣  Validando setup..."
python scripts/validate_setup.py

# 2. Rodar testes
echo ""
echo "2️⃣  Rodando testes..."
make test

# 3. Verificar sincronização
echo ""
echo "3️⃣  Testando sincronização..."
python scripts/import_data.py --auto --dry-run

# 4. Testar dashboard
echo ""
echo "4️⃣  Verificando dashboard..."
timeout 10s streamlit run app/dashboard.py --server.headless=true

# 5. Verificar automações
echo ""
echo "5️⃣  Verificando workflows do GitHub..."
ls -la .github/workflows/

# 6. Validar Docker
echo ""
echo "6️⃣  Validando Docker..."
docker-compose config

echo ""
echo "="*60
echo "✅ Checklist completo!"
echo "Revise qualquer item que falhou acima."