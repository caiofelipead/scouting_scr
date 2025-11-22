# Nome do arquivo: scripts/update_all.py

#!/usr/bin/env python3
"""
Script de atualização automática completa do Scout Pro
"""
import sys
import subprocess
import argparse
from pathlib import Path
from datetime import datetime

# Adiciona o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.logger import setup_logger
from src.config import Config

logger = setup_logger('update_all', 'updates.log')

def run_command(cmd: list, description: str) -> bool:
    """Executa um comando e loga o resultado"""
    logger.info(f"⏳ {description}...")
    try:
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True,
            cwd=Config.BASE_DIR
        )
        if result.stdout:
            logger.debug(result.stdout)
        logger.info(f"✅ {description} - Concluído")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ {description} - Erro: {e.stderr}")
        return False
    except Exception as e:
        logger.error(f"❌ {description} - Erro inesperado: {str(e)}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Atualização completa do Scout Pro')
    parser.add_argument('--skip-sync', action='store_true', help='Pula sincronização')
    parser.add_argument('--skip-photos', action='store_true', help='Pula download de fotos')
    parser.add_argument('--skip-clean', action='store_true', help='Pula limpeza')
    args = parser.parse_args()
    
    start_time = datetime.now()
    logger.info("="*60)
    logger.info("🚀 Iniciando atualização completa do Scout Pro")
    logger.info("="*60)
    
    steps = []
    
    if not args.skip_sync:
        steps.append((
            [sys.executable, "scripts/import_data.py", "--auto"],
            "Sincronização Google Sheets"
        ))
    
    if not args.skip_clean:
        steps.append((
            [sys.executable, "scripts/maintenance/limpar_duplicatas.py", "--auto"],
            "Limpeza de duplicatas"
        ))
    
    if not args.skip_photos:
        steps.append((
            [sys.executable, "scripts/maintenance/download_photos.py", "--missing-only"],
            "Download de fotos faltantes"
        ))
    
    # Executa todos os passos
    success_count = 0
    for cmd, description in steps:
        if run_command(cmd, description):
            success_count += 1
    
    # Resumo
    elapsed = datetime.now() - start_time
    logger.info("="*60)
    logger.info(f"📊 Resumo: {success_count}/{len(steps)} tarefas concluídas")
    logger.info(f"⏱️  Tempo total: {elapsed.total_seconds():.2f}s")
    logger.info("="*60)
    
    if success_count == len(steps):
        logger.info("✅ Atualização completa bem-sucedida!")
        return 0
    else:
        logger.warning("⚠️  Algumas tarefas falharam. Verifique os logs.")
        return 1

if __name__ == "__main__":
    sys.exit(main())