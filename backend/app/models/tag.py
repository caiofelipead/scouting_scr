"""
Modelos Tag e JogadorTag - Sistema de classificação
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func, PrimaryKeyConstraint
from sqlalchemy.orm import relationship

from ..core.database import Base


class Tag(Base):
    """Tabela de tags (etiquetas de classificação)"""
    __tablename__ = "tags"

    id_tag = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nome = Column(String(50), nullable=False, unique=True, index=True)
    cor = Column(String(20), default="#808080")  # Cor em hexadecimal
    descricao = Column(Text)

    # Relacionamento
    jogadores = relationship("JogadorTag", back_populates="tag", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Tag(id={self.id_tag}, nome='{self.nome}')>"


class JogadorTag(Base):
    """Tabela de relacionamento N:N entre jogadores e tags"""
    __tablename__ = "jogador_tags"

    id_jogador = Column(Integer, ForeignKey("jogadores.id_jogador", ondelete="CASCADE"), nullable=False)
    id_tag = Column(Integer, ForeignKey("tags.id_tag", ondelete="CASCADE"), nullable=False)
    adicionado_por = Column(String(100))
    adicionado_em = Column(DateTime(timezone=True), server_default=func.now())

    # Chave primária composta
    __table_args__ = (
        PrimaryKeyConstraint('id_jogador', 'id_tag'),
    )

    # Relacionamentos
    jogador = relationship("Jogador", back_populates="tags")
    tag = relationship("Tag", back_populates="jogadores")

    def __repr__(self):
        return f"<JogadorTag(jogador_id={self.id_jogador}, tag_id={self.id_tag})>"
