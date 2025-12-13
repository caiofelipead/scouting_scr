"""
Schemas Pydantic para Alerta
"""
from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field, ConfigDict


class AlertaBase(BaseModel):
    """Schema base para Alerta"""
    tipo_alerta: str = Field(..., min_length=1, max_length=100)
    descricao: Optional[str] = None
    prioridade: Optional[Literal["alta", "media", "baixa"]] = "media"
    ativo: bool = True


class AlertaCreate(AlertaBase):
    """Schema para criação de Alerta"""
    id_jogador: int = Field(..., gt=0)


class AlertaResponse(AlertaBase):
    """Schema de resposta para Alerta"""
    id_alerta: int
    id_jogador: int
    data_criacao: datetime

    model_config = ConfigDict(from_attributes=True)
