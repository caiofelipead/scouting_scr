"""
Modelo Wishlist - Lista de jogadores preferidos
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship

from ..core.database import Base


class Wishlist(Base):
    """Tabela de wishlist (jogadores desejados)"""
    __tablename__ = "wishlist"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_jogador = Column(Integer, ForeignKey("jogadores.id_jogador", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    prioridade = Column(String(20))  # 'alta', 'media', 'baixa'
    observacao = Column(Text)
    adicionado_por = Column(String(100))
    adicionado_em = Column(DateTime(timezone=True), server_default=func.now())

    # Relacionamento
    jogador = relationship("Jogador", back_populates="wishlist")

    def __repr__(self):
        return f"<Wishlist(id={self.id}, jogador_id={self.id_jogador}, prioridade='{self.prioridade}')>"
