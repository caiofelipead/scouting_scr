"""
Schemas Pydantic para Usuario e Autenticação
"""
from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UsuarioBase(BaseModel):
    """Schema base para Usuario"""
    username: str = Field(..., min_length=3, max_length=100)
    email: EmailStr
    nome: Optional[str] = Field(None, max_length=255)
    nivel: Literal["admin", "coordenador", "scout"] = "scout"


class UsuarioCreate(UsuarioBase):
    """Schema para criação de Usuario"""
    password: str = Field(..., min_length=6)


class UsuarioUpdate(BaseModel):
    """Schema para atualização de Usuario"""
    email: Optional[EmailStr] = None
    nome: Optional[str] = Field(None, max_length=255)
    nivel: Optional[Literal["admin", "coordenador", "scout"]] = None
    password: Optional[str] = Field(None, min_length=6)


class UsuarioResponse(UsuarioBase):
    """Schema de resposta para Usuario"""
    id: int
    ativo: bool
    data_criacao: datetime
    ultimo_acesso: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    """Schema de resposta para autenticação JWT"""
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    usuario: UsuarioResponse


class TokenPayload(BaseModel):
    """Payload do token JWT"""
    sub: int  # user_id
    exp: datetime
    username: str
    nivel: str


class LoginRequest(BaseModel):
    """Schema para requisição de login"""
    username: str
    password: str
