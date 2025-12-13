"""
Schemas Pydantic para Avaliacao
"""
from datetime import date, datetime
from typing import Optional
from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict, field_validator


class AvaliacaoBase(BaseModel):
    """Schema base para Avaliacao"""
    data_avaliacao: date
    nota_potencial: Optional[Decimal] = Field(None, ge=1.0, le=5.0)
    nota_tatico: Optional[Decimal] = Field(None, ge=1.0, le=5.0)
    nota_tecnico: Optional[Decimal] = Field(None, ge=1.0, le=5.0)
    nota_fisico: Optional[Decimal] = Field(None, ge=1.0, le=5.0)
    nota_mental: Optional[Decimal] = Field(None, ge=1.0, le=5.0)
    observacoes: Optional[str] = None
    avaliador: Optional[str] = Field(None, max_length=255)

    @field_validator('nota_potencial', 'nota_tatico', 'nota_tecnico', 'nota_fisico', 'nota_mental')
    @classmethod
    def round_to_one_decimal(cls, v):
        """Arredonda para 1 casa decimal"""
        if v is not None:
            return round(float(v), 1)
        return v


class AvaliacaoCreate(AvaliacaoBase):
    """Schema para criação de Avaliacao"""
    id_jogador: int = Field(..., gt=0)


class AvaliacaoResponse(AvaliacaoBase):
    """Schema de resposta para Avaliacao"""
    id: int
    id_jogador: int
    data_criacao: datetime

    model_config = ConfigDict(from_attributes=True)
