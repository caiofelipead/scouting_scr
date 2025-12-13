"""
Schemas Pydantic para Wishlist
"""
from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field, ConfigDict


class WishlistBase(BaseModel):
    """Schema base para Wishlist"""
    prioridade: Literal["alta", "media", "baixa"] = "media"
    observacao: Optional[str] = None
    adicionado_por: Optional[str] = Field(None, max_length=100)


class WishlistCreate(WishlistBase):
    """Schema para criação de Wishlist"""
    id_jogador: int = Field(..., gt=0)


class WishlistResponse(WishlistBase):
    """Schema de resposta para Wishlist"""
    id: int
    id_jogador: int
    adicionado_em: datetime

    model_config = ConfigDict(from_attributes=True)
