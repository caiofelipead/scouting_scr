#!/bin/bash
# Nome do arquivo: scripts/create_structure.sh

echo "📁 Criando nova estrutura de pastas..."

# Estrutura principal
mkdir -p src/{database,sync,scraping,utils,analysis}
mkdir -p app/{pages,components}
mkdir -p scripts/{setup,maintenance,reports}
mkdir -p tests/{unit,integration}
mkdir -p docs/{screenshots,guides,api}
mkdir -p data/{raw,processed,exports}
mkdir -p logs
mkdir -p backups
mkdir -p .github/workflows

# Criar arquivos __init__.py
touch src/__init__.py
touch src/database/__init__.py
touch src/sync/__init__.py
touch src/scraping/__init__.py
touch src/utils/__init__.py
touch src/analysis/__init__.py
touch app/__init__.py
touch tests/__init__.py

# Criar arquivo .gitkeep para pastas vazias
touch data/raw/.gitkeep
touch data/processed/.gitkeep
touch data/exports/.gitkeep
touch logs/.gitkeep
touch backups/.gitkeep
touch docs/screenshots/.gitkeep

echo "✅ Estrutura criada com sucesso!"