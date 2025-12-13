"""
Modelo VinculoClube - Relacionamento entre jogador e clube
"""
from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship

from ..core.database import Base


class VinculoClube(Base):
    """Tabela de vínculos entre jogadores e clubes"""
    __tablename__ = "vinculos_clubes"

    id_vinculo = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_jogador = Column(Integer, ForeignKey("jogadores.id_jogador", ondelete="CASCADE"), nullable=False, index=True)
    clube = Column(String(255))
    liga_clube = Column(String(255))
    posicao = Column(String(100), nullable=False)
    data_fim_contrato = Column(Date)
    status_contrato = Column(String(50))  # ex: "Ativo", "Livre", "Emprestado"
    data_criacao = Column(DateTime(timezone=True), server_default=func.now())
    data_atualizacao = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relacionamento
    jogador = relationship("Jogador", back_populates="vinculos")

    def __repr__(self):
        return f"<VinculoClube(id={self.id_vinculo}, jogador_id={self.id_jogador}, clube='{self.clube}')>"
