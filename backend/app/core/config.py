"""
Configurações centralizadas do Backend - Scout Pro API
"""
from typing import Optional
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Configurações da aplicação carregadas de variáveis de ambiente"""

    # Aplicação
    APP_NAME: str = "Scout Pro API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Banco de Dados PostgreSQL
    DATABASE_URL: str
    DB_POOL_SIZE: int = 15
    DB_MAX_OVERFLOW: int = 5
    DB_POOL_RECYCLE: int = 3600

    # JWT Authentication
    SECRET_KEY: str = "your-super-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:5173",  # Vite default
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]

    # Paginação
    DEFAULT_PAGE_SIZE: int = 50
    MAX_PAGE_SIZE: int = 200

    # Cache (Redis opcional)
    REDIS_URL: Optional[str] = None
    CACHE_TTL: int = 3600  # 1 hora

    # Upload de fotos
    UPLOAD_DIR: str = "fotos"
    MAX_UPLOAD_SIZE: int = 5 * 1024 * 1024  # 5MB
    ALLOWED_EXTENSIONS: set[str] = {"jpg", "jpeg", "png", "webp"}

    # Google Sheets (sincronização)
    GOOGLE_CREDENTIALS_PATH: Optional[str] = None
    SPREADSHEET_ID: Optional[str] = None

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Retorna configurações em cache (singleton)"""
    return Settings()


# Instância global
settings = get_settings()
