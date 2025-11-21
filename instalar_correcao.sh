#!/bin/bash

# Script de Instalação Automática do Dashboard Corrigido
# Execute: bash instalar_correcao.sh

echo "=============================================="
echo "🚀 INSTALAÇÃO DO DASHBOARD CORRIGIDO"
echo "=============================================="
echo ""

# 1. Verificar se os arquivos existem
echo "📦 Verificando arquivos necessários..."

if [ ! -f "dashboard_COMPLETO_CORRIGIDO.py" ]; then
    echo "❌ Arquivo dashboard_COMPLETO_CORRIGIDO.py não encontrado!"
    echo "   Faça o upload deste arquivo primeiro."
    exit 1
fi

if [ ! -f "database_corrigido.py" ]; then
    echo "❌ Arquivo database_corrigido.py não encontrado!"
    echo "   Faça o upload deste arquivo primeiro."
    exit 1
fi

if [ ! -f "recriar_tabela_avaliacoes.py" ]; then
    echo "❌ Arquivo recriar_tabela_avaliacoes.py não encontrado!"
    echo "   Faça o upload deste arquivo primeiro."
    exit 1
fi

echo "✅ Todos os arquivos necessários encontrados!"
echo ""

# 2. Fazer backup
echo "💾 Fazendo backup dos arquivos antigos..."
if [ -f "dashboard.py" ]; then
    cp dashboard.py dashboard_backup_$(date +%Y%m%d_%H%M%S).py
    echo "   ✓ Backup de dashboard.py criado"
fi

if [ -f "database.py" ]; then
    cp database.py database_backup_$(date +%Y%m%d_%H%M%S).py
    echo "   ✓ Backup de database.py criado"
fi

if [ -f "scouting.db" ]; then
    cp scouting.db scouting_backup_$(date +%Y%m%d_%H%M%S).db
    echo "   ✓ Backup de scouting.db criado"
fi
echo ""

# 3. Substituir arquivos
echo "🔄 Substituindo arquivos..."
cp dashboard_COMPLETO_CORRIGIDO.py dashboard.py
echo "   ✓ dashboard.py atualizado"

cp database_corrigido.py database.py
echo "   ✓ database.py atualizado"
echo ""

# 4. Recriar tabela
echo "🏗️  Recriando tabela de avaliações..."
python recriar_tabela_avaliacoes.py
echo ""

# 5. Verificar instalação
echo "✅ Verificando instalação..."
if [ -f "dashboard.py" ] && [ -f "database.py" ] && [ -f "scouting.db" ]; then
    echo "   ✓ Todos os arquivos estão no lugar"
else
    echo "   ⚠️  Alguns arquivos podem estar faltando"
fi
echo ""

echo "=============================================="
echo "✅ INSTALAÇÃO CONCLUÍDA COM SUCESSO!"
echo "=============================================="
echo ""
echo "🎯 Próximo passo:"
echo "   Execute: streamlit run dashboard.py"
echo ""
echo "📊 Teste criando uma avaliação de jogador!"
echo ""
