"""
Modelo Proposta - Propostas de transferência
"""
from sqlalchemy import Column, Integer, String, Numeric, Date, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship

from ..core.database import Base


class Proposta(Base):
    """Tabela de propostas de transferência"""
    __tablename__ = "propostas"

    id_proposta = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_jogador = Column(Integer, ForeignKey("jogadores.id_jogador", ondelete="CASCADE"), nullable=False, index=True)
    valor_proposta = Column(Numeric(12, 2))
    moeda = Column(String(10), default="BRL")
    tipo_transferencia = Column(String(50), default="Definitiva")  # 'Definitiva', 'Emprestimo'
    clube_interessado = Column(String(255))
    data_proposta = Column(Date, server_default=func.current_date())
    status = Column(String(50), default="Em análise")  # 'Em análise', 'Aceita', 'Recusada'
    observacoes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relacionamento
    jogador = relationship("Jogador", back_populates="propostas")

    def __repr__(self):
        return f"<Proposta(id={self.id_proposta}, jogador_id={self.id_jogador}, valor={self.valor_proposta})>"
