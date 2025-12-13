"""
Modelo Usuario - Sistema de autenticação
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, func

from ..core.database import Base


class Usuario(Base):
    """Tabela de usuários do sistema"""
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    nome = Column(String(255))
    senha_hash = Column(String(255), nullable=False)  # Bcrypt hash
    nivel = Column(String(50), default="scout")  # 'admin', 'coordenador', 'scout'
    ativo = Column(Boolean, default=True)
    data_criacao = Column(DateTime(timezone=True), server_default=func.now())
    ultimo_acesso = Column(DateTime(timezone=True))

    def __repr__(self):
        return f"<Usuario(id={self.id}, username='{self.username}', nivel='{self.nivel}')>"
