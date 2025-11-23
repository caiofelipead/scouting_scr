# Nome do arquivo: scripts/scheduler.py

#!/usr/bin/env python3
"""
Scheduler que roda tarefas em background
"""
import subprocess
import sys
import time
from pathlib import Path

import schedule

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import Config
from src.utils.logger import setup_logger

logger = setup_logger("scheduler", "scheduler.log")


def run_script(script_path: str, description: str):
    """Executa um script Python"""
    logger.info(f"🔄 Iniciando: {description}")
    try:
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            cwd=Config.BASE_DIR,
        )

        if result.returncode == 0:
            logger.info(f"✅ {description} - Concluído")
        else:
            logger.error(f"❌ {description} - Erro: {result.stderr}")

    except Exception as e:
        logger.error(f"❌ {description} - Exceção: {e}")


def sync_google_sheets():
    """Sincroniza dados do Google Sheets"""
    run_script("scripts/import_data.py", "Sincronização Google Sheets")


def download_photos():
    """Baixa fotos faltantes"""
    run_script("scripts/maintenance/download_photos.py", "Download de fotos")


def check_contracts():
    """Verifica contratos expirando"""
    run_script("scripts/maintenance/check_contracts.py", "Verificação de contratos")


def backup_database():
    """Faz backup do banco"""
    run_script("scripts/maintenance/backup.py", "Backup do banco de dados")


def setup_schedule():
    """Configura todos os agendamentos"""

    # Sincronização diária
    sync_time = Config.DAILY_SYNC_TIME
    schedule.every().day.at(sync_time).do(sync_google_sheets)
    logger.info(f"📅 Sincronização agendada para {sync_time}")

    # Fotos a cada 6 horas
    schedule.every(6).hours.do(download_photos)
    logger.info("📅 Download de fotos a cada 6 horas")

    # Contratos toda segunda às 9h
    schedule.every().monday.at("09:00").do(check_contracts)
    logger.info("📅 Verificação de contratos: segunda às 9h")

    # Backup semanal
    backup_day = Config.WEEKLY_BACKUP_DAY
    getattr(schedule.every(), backup_day).at("23:00").do(backup_database)
    logger.info(f"📅 Backup: {backup_day} às 23h")


def main():
    """Loop principal do scheduler"""
    logger.info("=" * 60)
    logger.info("🚀 Scout Pro Scheduler Iniciado")
    logger.info("=" * 60)

    setup_schedule()

    logger.info("\n📋 Tarefas agendadas:")
    for job in schedule.get_jobs():
        logger.info(f"  • {job}")

    logger.info("\n⏰ Aguardando próxima tarefa...\n")

    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Verifica a cada minuto

    except KeyboardInterrupt:
        logger.info("\n⏹️  Scheduler interrompido pelo usuário")
        sys.exit(0)

    except Exception as e:
        logger.error(f"Erro no scheduler: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
