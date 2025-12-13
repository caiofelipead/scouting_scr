"""
Schemas Pydantic para VinculoClube
"""
from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class VinculoClubeBase(BaseModel):
    """Schema base para VinculoClube"""
    clube: Optional[str] = Field(None, max_length=255)
    liga_clube: Optional[str] = Field(None, max_length=255)
    posicao: str = Field(..., min_length=1, max_length=100)
    data_fim_contrato: Optional[date] = None
    status_contrato: Optional[str] = Field(None, max_length=50)


class VinculoClubeCreate(VinculoClubeBase):
    """Schema para criação de VinculoClube"""
    id_jogador: int = Field(..., gt=0)


class VinculoClubeResponse(VinculoClubeBase):
    """Schema de resposta para VinculoClube"""
    id_vinculo: int
    id_jogador: int
    data_criacao: datetime
    data_atualizacao: datetime

    model_config = ConfigDict(from_attributes=True)
