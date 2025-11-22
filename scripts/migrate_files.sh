#!/bin/bash
# Nome do arquivo: scripts/migrate_files.sh

echo "🔄 Migrando arquivos para nova estrutura..."

# Backup antes de mover
echo "📦 Criando backup adicional..."
cp -r . ../scouting_scr_pre_migration

# Mover arquivos Python principais
echo "📝 Movendo arquivos de código..."

# Database
mv database.py src/database/database.py 2>/dev/null || echo "database.py já movido"

# Sync
mv google_sheets_sync.py src/sync/google_sheets_sync.py 2>/dev/null || echo "google_sheets_sync.py já movido"

# Scraping
mv baixar_fotos_scraping.py src/scraping/transfermarkt_scraper.py 2>/dev/null || echo "baixar_fotos_scraping.py já movido"

# Dashboard
mv dashboard.py app/dashboard.py 2>/dev/null || echo "dashboard.py já movido"

# Scripts de manutenção
mv import_data.py scripts/import_data.py 2>/dev/null || echo "import_data.py já movido"
mv limpar_duplicatas.py scripts/maintenance/limpar_duplicatas.py 2>/dev/null || echo "limpar_duplicatas.py já movido"

echo "✅ Migração básica concluída!"
echo "⚠️  Verifique se todos os arquivos foram movidos corretamente"