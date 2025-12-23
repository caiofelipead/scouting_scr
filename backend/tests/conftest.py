"""
Configuração global de testes Pytest
"""
import pytest
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.core.database import Base, get_db
from app.main import app

# URL de banco de testes (use in-memory SQLite para testes rápidos)
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}  # Necessário para SQLite
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    """
    Fixture que fornece uma sessão de banco de dados para testes.
    Cria todas as tabelas antes e limpa depois.
    """
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def override_get_db(db_session: Session):
    """
    Fixture que sobrescreve a dependência get_db para usar o banco de testes.
    """
    def _get_test_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = _get_test_db
    yield
    app.dependency_overrides.clear()


@pytest.fixture(scope="session")
def test_client():
    """
    Fixture que fornece um TestClient para testes de API.
    """
    from fastapi.testclient import TestClient
    return TestClient(app)
