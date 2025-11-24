#!/bin/bash
# Corrigir mapeamento de colunas no database.py

echo "🔧 Corrigindo database.py..."

# Backup
cp database.py database.py.bak

# Corrigir 'Pé' para 'Pé dominante'
sed -i "s/row.get('Pé', '')/row.get('Pé dominante', '')/g" database.py

# Corrigir 'Fim de contrato' para 'Fim de Contrato' 
sed -i "s/row.get('Fim de contrato')/row.get('Fim de Contrato')/g" database.py

echo "✅ Correções aplicadas!"
echo ""
echo "📝 Verificando mudanças:"
grep -n "Pé dominante" database.py
grep -n "Fim de Contrato" database.py
