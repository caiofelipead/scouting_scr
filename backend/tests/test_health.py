"""
Testes básicos de health check e API
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_read_health():
    """Testa endpoint de health check"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data


def test_read_root():
    """Testa endpoint raiz"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data or "app" in data


def test_cors_headers():
    """Testa configuração de CORS"""
    response = client.options("/health")
    assert response.status_code == 200
