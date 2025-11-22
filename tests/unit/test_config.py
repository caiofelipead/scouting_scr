import pytest
import sys
from pathlib import Path

# Adiciona o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.config import Config

def test_config_paths():
    """Testa se os paths estão configurados"""
    assert Config.BASE_DIR.exists()
    assert Config.DATA_DIR is not None

def test_config_ensure_dirs():
    """Testa criação de diretórios"""
    Config.ensure_dirs()
    assert Config.LOGS_DIR.exists()
    assert Config.BACKUPS_DIR.exists()
