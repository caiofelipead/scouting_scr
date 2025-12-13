"""
Modelo BuscaSalva - Filtros salvos pelo usuário
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, func

from ..core.database import Base


class BuscaSalva(Base):
    """Tabela de buscas/filtros salvos"""
    __tablename__ = "buscas_salvas"

    id_busca = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nome_busca = Column(String(100), nullable=False)
    filtros = Column(Text, nullable=False)  # JSON serializado com os filtros
    criado_por = Column(String(100))
    criado_em = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<BuscaSalva(id={self.id_busca}, nome='{self.nome_busca}')>"
