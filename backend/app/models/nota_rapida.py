"""
Modelo NotaRapida - Observações rápidas sobre jogadores
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship

from ..core.database import Base


class NotaRapida(Base):
    """Tabela de notas rápidas sobre jogadores"""
    __tablename__ = "notas_rapidas"

    id_nota = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_jogador = Column(Integer, ForeignKey("jogadores.id_jogador", ondelete="CASCADE"), nullable=False, index=True)
    texto = Column(Text, nullable=False)
    autor = Column(String(100))
    tipo = Column(String(50), default="observacao")  # 'observacao', 'destaque', 'ponto_atencao'
    data_nota = Column(DateTime(timezone=True), server_default=func.now())

    # Relacionamento
    jogador = relationship("Jogador", back_populates="notas_rapidas")

    def __repr__(self):
        return f"<NotaRapida(id={self.id_nota}, jogador_id={self.id_jogador})>"
