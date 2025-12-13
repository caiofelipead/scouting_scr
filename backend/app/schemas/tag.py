"""
Schemas Pydantic para Tag
"""
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class TagBase(BaseModel):
    """Schema base para Tag"""
    nome: str = Field(..., min_length=1, max_length=50)
    cor: Optional[str] = Field("#808080", pattern=r"^#[0-9A-Fa-f]{6}$")
    descricao: Optional[str] = None


class TagCreate(TagBase):
    """Schema para criação de Tag"""
    pass


class TagResponse(TagBase):
    """Schema de resposta para Tag"""
    id_tag: int

    model_config = ConfigDict(from_attributes=True)
