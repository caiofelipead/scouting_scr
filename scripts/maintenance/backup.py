# Nome do arquivo: scripts/maintenance/backup.py

#!/usr/bin/env python3
"""
Script de backup automático
"""
import shutil
import sys
import tarfile
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.config import Config
from src.utils.logger import setup_logger

logger = setup_logger("backup", "backup.log")


def create_backup():
    """Cria backup completo do sistema"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    logger.info("=" * 60)
    logger.info("💾 Iniciando backup do Scout Pro")
    logger.info("=" * 60)

    success = True

    # Backup do banco de dados
    if Config.DB_PATH.exists():
        backup_db = Config.BACKUPS_DIR / f"scouting_{timestamp}.db"
        try:
            shutil.copy2(Config.DB_PATH, backup_db)
            logger.info(f"✅ Banco de dados: {backup_db.name}")
        except Exception as e:
            logger.error(f"❌ Erro ao copiar banco: {e}")
            success = False
    else:
        logger.warning("⚠️  Banco de dados não encontrado")

    # Backup das fotos (compactado)
    if Config.PHOTOS_DIR.exists() and any(Config.PHOTOS_DIR.iterdir()):
        backup_photos = Config.BACKUPS_DIR / f"fotos_{timestamp}.tar.gz"
        try:
            with tarfile.open(backup_photos, "w:gz") as tar:
                tar.add(Config.PHOTOS_DIR, arcname="fotos")
            logger.info(f"✅ Fotos: {backup_photos.name}")
        except Exception as e:
            logger.error(f"❌ Erro ao compactar fotos: {e}")
            success = False
    else:
        logger.warning("⚠️  Pasta de fotos vazia ou não encontrada")

    # Limpa backups antigos (mantém últimos 10)
    cleanup_old_backups(keep=10)

    logger.info("=" * 60)
    if success:
        logger.info("✅ Backup concluído com sucesso!")
    else:
        logger.warning("⚠️  Backup concluído com alguns erros")
    logger.info("=" * 60)

    return success


def cleanup_old_backups(keep: int = 10):
    """Remove backups antigos, mantendo os N mais recentes"""
    try:
        # Lista todos os backups
        db_backups = sorted(Config.BACKUPS_DIR.glob("scouting_*.db"), reverse=True)
        photo_backups = sorted(Config.BACKUPS_DIR.glob("fotos_*.tar.gz"), reverse=True)

        # Remove backups excedentes
        removed_count = 0
        for backup in db_backups[keep:]:
            backup.unlink()
            removed_count += 1

        for backup in photo_backups[keep:]:
            backup.unlink()
            removed_count += 1

        if removed_count > 0:
            logger.info(f"🗑️  Removidos {removed_count} backups antigos")

    except Exception as e:
        logger.error(f"Erro ao limpar backups antigos: {e}")


if __name__ == "__main__":
    sys.exit(0 if create_backup() else 1)
