"""
Schemas Pydantic - Validação de entrada/saída
"""
from .jogador import (
    JogadorBase,
    JogadorCreate,
    JogadorUpdate,
    JogadorResponse,
    JogadorWithDetails,
)
from .vinculo import VinculoClubeBase, VinculoClubeCreate, VinculoClubeResponse
from .avaliacao import AvaliacaoBase, AvaliacaoCreate, AvaliacaoResponse
from .tag import TagBase, TagCreate, TagResponse
from .wishlist import WishlistBase, WishlistCreate, WishlistResponse
from .alerta import AlertaBase, AlertaCreate, AlertaResponse
from .nota_rapida import NotaRapidaBase, NotaRapidaCreate, NotaRapidaResponse
from .proposta import PropostaBase, PropostaCreate, PropostaResponse
from .usuario import UsuarioBase, UsuarioCreate, UsuarioResponse, Token

__all__ = [
    "JogadorBase",
    "JogadorCreate",
    "JogadorUpdate",
    "JogadorResponse",
    "JogadorWithDetails",
    "VinculoClubeBase",
    "VinculoClubeCreate",
    "VinculoClubeResponse",
    "AvaliacaoBase",
    "AvaliacaoCreate",
    "AvaliacaoResponse",
    "TagBase",
    "TagCreate",
    "TagResponse",
    "WishlistBase",
    "WishlistCreate",
    "WishlistResponse",
    "AlertaBase",
    "AlertaCreate",
    "AlertaResponse",
    "NotaRapidaBase",
    "NotaRapidaCreate",
    "NotaRapidaResponse",
    "PropostaBase",
    "PropostaCreate",
    "PropostaResponse",
    "UsuarioBase",
    "UsuarioCreate",
    "UsuarioResponse",
    "Token",
]
