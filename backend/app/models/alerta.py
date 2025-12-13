"""
Modelo Alerta - Sistema de notificações
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship

from ..core.database import Base


class Alerta(Base):
    """Tabela de alertas sobre jogadores"""
    __tablename__ = "alertas"

    id_alerta = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_jogador = Column(Integer, ForeignKey("jogadores.id_jogador", ondelete="CASCADE"), nullable=False, index=True)
    tipo_alerta = Column(String(100), nullable=False)  # ex: "Contrato expirando", "Lesão"
    descricao = Column(Text)
    prioridade = Column(String(50))  # 'alta', 'media', 'baixa'
    data_criacao = Column(DateTime(timezone=True), server_default=func.now())
    ativo = Column(Boolean, default=True, index=True)

    # Relacionamento
    jogador = relationship("Jogador", back_populates="alertas")

    def __repr__(self):
        return f"<Alerta(id={self.id_alerta}, tipo='{self.tipo_alerta}', ativo={self.ativo})>"
