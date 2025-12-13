"""
Schemas Pydantic para NotaRapida
"""
from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field, ConfigDict


class NotaRapidaBase(BaseModel):
    """Schema base para NotaRapida"""
    texto: str = Field(..., min_length=1)
    autor: Optional[str] = Field(None, max_length=100)
    tipo: Literal["observacao", "destaque", "ponto_atencao"] = "observacao"


class NotaRapidaCreate(NotaRapidaBase):
    """Schema para criação de NotaRapida"""
    id_jogador: int = Field(..., gt=0)


class NotaRapidaResponse(NotaRapidaBase):
    """Schema de resposta para NotaRapida"""
    id_nota: int
    id_jogador: int
    data_nota: datetime

    model_config = ConfigDict(from_attributes=True)
