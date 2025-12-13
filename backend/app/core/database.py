"""
Configuração de Banco de Dados - PostgreSQL
"""
from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool

from .config import settings

# Engine do PostgreSQL com pool de conexões
engine = create_engine(
    settings.DATABASE_URL,
    poolclass=QueuePool,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_recycle=settings.DB_POOL_RECYCLE,
    pool_pre_ping=True,  # Verifica conexões antes de usar
    echo=settings.DEBUG,  # Log SQL em modo debug
    connect_args={
        "sslmode": "require",  # SSL obrigatório (Railway)
        "options": "-c timezone=utc"
    }
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para modelos SQLAlchemy
Base = declarative_base()


# Dependency para FastAPI
def get_db():
    """Dependency que fornece sessão do banco de dados"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Event listeners para otimização
@event.listens_for(engine, "connect")
def receive_connect(dbapi_conn, connection_record):
    """Executado quando uma nova conexão é criada"""
    # Configurações específicas do PostgreSQL
    connection_record.info['pid'] = dbapi_conn.get_backend_pid()


@event.listens_for(engine, "checkout")
def receive_checkout(dbapi_conn, connection_record, connection_proxy):
    """Executado quando uma conexão é retirada do pool"""
    pass  # Pode adicionar logging se necessário
