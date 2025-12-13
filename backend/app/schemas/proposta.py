"""
Schemas Pydantic para Proposta
"""
from datetime import date, datetime
from typing import Optional, Literal
from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict


class PropostaBase(BaseModel):
    """Schema base para Proposta"""
    valor_proposta: Optional[Decimal] = Field(None, ge=0)
    moeda: str = Field("BRL", max_length=10)
    tipo_transferencia: Literal["Definitiva", "Emprestimo"] = "Definitiva"
    clube_interessado: Optional[str] = Field(None, max_length=255)
    data_proposta: Optional[date] = None
    status: Literal["Em análise", "Aceita", "Recusada"] = "Em análise"
    observacoes: Optional[str] = None


class PropostaCreate(PropostaBase):
    """Schema para criação de Proposta"""
    id_jogador: int = Field(..., gt=0)


class PropostaResponse(PropostaBase):
    """Schema de resposta para Proposta"""
    id_proposta: int
    id_jogador: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
