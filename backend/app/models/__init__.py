"""
Modelos SQLAlchemy - Scout Pro
"""
from .jogador import Jogador
from .vinculo import VinculoClube
from .avaliacao import Avaliacao
from .tag import Tag, JogadorTag
from .wishlist import Wishlist
from .alerta import Alerta
from .nota_rapida import NotaRapida
from .busca_salva import BuscaSalva
from .proposta import Proposta
from .usuario import Usuario

__all__ = [
    "Jogador",
    "VinculoClube",
    "Avaliacao",
    "Tag",
    "JogadorTag",
    "Wishlist",
    "Alerta",
    "NotaRapida",
    "BuscaSalva",
    "Proposta",
    "Usuario",
]
