"""
Modelo Jogador - Representa um jogador no banco de dados
"""
from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.orm import relationship

from ..core.database import Base


class Jogador(Base):
    """Tabela de jogadores"""
    __tablename__ = "jogadores"

    id_jogador = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nome = Column(String(255), nullable=False, index=True)
    nacionalidade = Column(String(100))
    ano_nascimento = Column(Integer)
    idade_atual = Column(Integer)
    altura = Column(Integer)  # em cm
    pe_dominante = Column(String(50))
    transfermarkt_id = Column(String(100), unique=True, index=True)
    data_criacao = Column(DateTime(timezone=True), server_default=func.now())
    data_atualizacao = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relacionamentos
    vinculos = relationship("VinculoClube", back_populates="jogador", cascade="all, delete-orphan")
    avaliacoes = relationship("Avaliacao", back_populates="jogador", cascade="all, delete-orphan")
    tags = relationship("JogadorTag", back_populates="jogador", cascade="all, delete-orphan")
    wishlist = relationship("Wishlist", back_populates="jogador", uselist=False, cascade="all, delete-orphan")
    alertas = relationship("Alerta", back_populates="jogador", cascade="all, delete-orphan")
    notas_rapidas = relationship("NotaRapida", back_populates="jogador", cascade="all, delete-orphan")
    propostas = relationship("Proposta", back_populates="jogador", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Jogador(id={self.id_jogador}, nome='{self.nome}')>"
