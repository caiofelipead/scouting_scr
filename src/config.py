import os
from pathlib import Path

from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()


class Config:
    """Configurações centralizadas do Scout Pro"""

    # Diretórios
    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = BASE_DIR / "data"
    LOGS_DIR = BASE_DIR / "logs"
    BACKUPS_DIR = BASE_DIR / "backups"
    PHOTOS_DIR = BASE_DIR / os.getenv("PHOTOS_DIR", "fotos")

    # Google Sheets
    GOOGLE_CREDENTIALS_PATH = BASE_DIR / os.getenv(
        "GOOGLE_CREDENTIALS_PATH", "credentials.json"
    )
    SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
    SHEET_NAME = os.getenv("SHEET_NAME", "Planilha1")

    # Database
    DB_NAME = os.getenv("DB_NAME", "scouting.db")
    DB_PATH = DATA_DIR / DB_NAME

    # Transfermarkt
    TM_DELAY = float(os.getenv("TM_DELAY", "1.5"))
    TM_MAX_RETRIES = int(os.getenv("TM_MAX_RETRIES", "3"))
    TM_BASE_URL = "https://www.transfermarkt.com.br"

    # Notificações
    EMAIL_ENABLED = os.getenv("EMAIL_ENABLED", "false").lower() == "true"
    EMAIL_USER = os.getenv("EMAIL_USER")
    EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
    NOTIFY_EMAIL = os.getenv("NOTIFY_EMAIL")

    TELEGRAM_ENABLED = os.getenv("TELEGRAM_ENABLED", "false").lower() == "true"
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

    # Dashboard
    DASHBOARD_PORT = int(os.getenv("DASHBOARD_PORT", "8501"))
    DASHBOARD_HOST = os.getenv("DASHBOARD_HOST", "0.0.0.0")
    AUTO_REFRESH = os.getenv("AUTO_REFRESH", "true").lower() == "true"
    REFRESH_INTERVAL = int(os.getenv("REFRESH_INTERVAL", "300"))

    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = LOGS_DIR / os.getenv("LOG_FILE", "scout_pro.log")

    # Debug
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    VERBOSE = os.getenv("VERBOSE", "false").lower() == "true"

    @classmethod
    def ensure_dirs(cls):
        """Cria diretórios necessários se não existirem"""
        for dir_path in [cls.DATA_DIR, cls.LOGS_DIR, cls.BACKUPS_DIR, cls.PHOTOS_DIR]:
            dir_path.mkdir(parents=True, exist_ok=True)

    @classmethod
    def validate(cls):
        """Valida configurações essenciais"""
        errors = []

        if not cls.GOOGLE_CREDENTIALS_PATH.exists():
            errors.append(
                f"❌ Arquivo de credenciais não encontrado: {cls.GOOGLE_CREDENTIALS_PATH}"
            )

        if not cls.SPREADSHEET_ID:
            errors.append("❌ SPREADSHEET_ID não configurado no .env")

        if cls.EMAIL_ENABLED and not (cls.EMAIL_USER and cls.EMAIL_PASSWORD):
            errors.append("❌ Email habilitado mas credenciais não configuradas")

        if errors:
            print("\n⚠️  ERROS DE CONFIGURAÇÃO:")
            for error in errors:
                print(f"  {error}")
            return False

        print("✅ Configurações válidas!")
        return True


# Inicialização
Config.ensure_dirs()
