"""
Modelo Avaliacao - Avaliações multidimensionais de jogadores
"""
from sqlalchemy import Column, Integer, String, Date, Numeric, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship

from ..core.database import Base


class Avaliacao(Base):
    """Tabela de avaliações dos jogadores"""
    __tablename__ = "avaliacoes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_jogador = Column(Integer, ForeignKey("jogadores.id_jogador", ondelete="CASCADE"), nullable=False, index=True)
    data_avaliacao = Column(Date, nullable=False)

    # Notas multidimensionais (1-5)
    nota_potencial = Column(Numeric(3, 1))  # Potencial geral
    nota_tatico = Column(Numeric(3, 1))     # Dimensão tática
    nota_tecnico = Column(Numeric(3, 1))    # Dimensão técnica
    nota_fisico = Column(Numeric(3, 1))     # Dimensão física
    nota_mental = Column(Numeric(3, 1))     # Dimensão mental

    observacoes = Column(Text)
    avaliador = Column(String(255))  # Quem fez a avaliação
    data_criacao = Column(DateTime(timezone=True), server_default=func.now())

    # Relacionamento
    jogador = relationship("Jogador", back_populates="avaliacoes")

    def __repr__(self):
        return f"<Avaliacao(id={self.id}, jogador_id={self.id_jogador}, potencial={self.nota_potencial})>"
