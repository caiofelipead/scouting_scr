#!/bin/bash
# Script para corrigir mapeamento de colunas

echo "🔧 Corrigindo mapeamento de colunas..."

# Fazer backup
cp google_sheets_sync_railway.py google_sheets_sync_railway.py.bak

# Corrigir 'Pé' para 'Pé dominante'
sed -i "s/row.get('Pé', '')/row.get('Pé dominante', '')/g" google_sheets_sync_railway.py

# Corrigir 'Fim de contrato' para 'Fim de Contrato'
sed -i "s/row.get('Fim de contrato')/row.get('Fim de Contrato')/g" google_sheets_sync_railway.py

echo "✅ Correções aplicadas!"
echo ""
echo "📝 Verificando mudanças:"
grep -n "row.get('Pé dominante" google_sheets_sync_railway.py
grep -n "row.get('Fim de Contrato" google_sheets_sync_railway.py
