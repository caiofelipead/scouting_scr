# Nome do arquivo: scripts/setup/fix_imports.py

import os
from pathlib import Path


def fix_imports_in_file(file_path):
    """Atualiza imports em um arquivo Python"""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Mapeamento de imports antigos -> novos
    replacements = {
        "from src.database.database import": "from src.database.database import",
        "import src.database.database as database": "import src.database.database as database",
        "from src.sync.google_sheets_sync import": "from src.sync.google_sheets_sync import",
        "import src.sync.google_sheets_sync as google_sheets_sync": "import src.sync.google_sheets_sync as google_sheets_sync",
        "from src.scraping.transfermarkt_scraper import": "from src.scraping.transfermarkt_scraper import",
    }

    modified = False
    for old, new in replacements.items():
        if old in content:
            content = content.replace(old, new)
            modified = True

    if modified:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return True
    return False


def main():
    """Processa todos os arquivos Python"""
    project_root = Path(__file__).parent.parent.parent

    print("🔧 Atualizando imports...")

    updated = 0
    for root, dirs, files in os.walk(project_root):
        # Ignora diretórios específicos
        dirs[:] = [d for d in dirs if d not in ["venv", ".venv", "__pycache__", ".git"]]

        for file in files:
            if file.endswith(".py"):
                file_path = Path(root) / file
                if fix_imports_in_file(file_path):
                    print(f"  ✅ {file_path.relative_to(project_root)}")
                    updated += 1

    print(f"\n✅ {updated} arquivos atualizados")


if __name__ == "__main__":
    main()
