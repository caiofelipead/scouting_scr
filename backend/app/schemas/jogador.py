"""
Schemas Pydantic para Jogador
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class JogadorBase(BaseModel):
    """Schema base para Jogador"""
    nome: str = Field(..., min_length=1, max_length=255)
    nacionalidade: Optional[str] = Field(None, max_length=100)
    ano_nascimento: Optional[int] = Field(None, ge=1950, le=2020)
    idade_atual: Optional[int] = Field(None, ge=14, le=50)
    altura: Optional[int] = Field(None, ge=150, le=220, description="Altura em cm")
    pe_dominante: Optional[str] = Field(None, max_length=50)
    transfermarkt_id: Optional[str] = Field(None, max_length=100)


class JogadorCreate(JogadorBase):
    """Schema para criação de Jogador"""
    pass


class JogadorUpdate(BaseModel):
    """Schema para atualização de Jogador (todos os campos opcionais)"""
    nome: Optional[str] = Field(None, min_length=1, max_length=255)
    nacionalidade: Optional[str] = Field(None, max_length=100)
    ano_nascimento: Optional[int] = Field(None, ge=1950, le=2020)
    idade_atual: Optional[int] = Field(None, ge=14, le=50)
    altura: Optional[int] = Field(None, ge=150, le=220)
    pe_dominante: Optional[str] = Field(None, max_length=50)
    transfermarkt_id: Optional[str] = Field(None, max_length=100)


class JogadorResponse(JogadorBase):
    """Schema de resposta para Jogador"""
    id_jogador: int
    data_criacao: datetime
    data_atualizacao: datetime

    model_config = ConfigDict(from_attributes=True)


class JogadorWithDetails(JogadorResponse):
    """Schema de resposta com detalhes completos (relacionamentos)"""
    clube: Optional[str] = None
    liga_clube: Optional[str] = None
    posicao: Optional[str] = None
    status_contrato: Optional[str] = None
    data_fim_contrato: Optional[str] = None
    em_wishlist: bool = False
    nota_potencial_media: Optional[float] = None
    total_avaliacoes: int = 0

    model_config = ConfigDict(from_attributes=True)
