"""
CRUD Operations para Wishlist
"""
from typing import Optional, List
from sqlalchemy.orm import Session, joinedload

from ..models.wishlist import Wishlist
from ..models.jogador import Jogador
from ..models.vinculo import VinculoClube
from ..schemas.wishlist import WishlistCreate


def get_wishlist(
    db: Session,
    prioridade: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
) -> List[Wishlist]:
    """Lista jogadores na wishlist (com jogador carregado)"""
    query = db.query(Wishlist).options(
        joinedload(Wishlist.jogador).joinedload(Jogador.vinculos)
    )

    if prioridade:
        query = query.filter(Wishlist.prioridade == prioridade)

    return query.offset(skip).limit(limit).all()


def get_wishlist_item(db: Session, wishlist_id: int) -> Optional[Wishlist]:
    """Busca item da wishlist por ID"""
    return db.query(Wishlist).filter(Wishlist.id == wishlist_id).first()


def get_wishlist_by_jogador(db: Session, jogador_id: int) -> Optional[Wishlist]:
    """Verifica se jogador está na wishlist"""
    return db.query(Wishlist).filter(Wishlist.id_jogador == jogador_id).first()


def create_wishlist_item(db: Session, wishlist: WishlistCreate) -> Wishlist:
    """Adiciona jogador à wishlist"""
    db_wishlist = Wishlist(**wishlist.model_dump())
    db.add(db_wishlist)
    db.commit()
    db.refresh(db_wishlist)
    return db_wishlist


def delete_wishlist_item(db: Session, jogador_id: int) -> bool:
    """Remove jogador da wishlist"""
    db_wishlist = get_wishlist_by_jogador(db, jogador_id)
    if not db_wishlist:
        return False

    db.delete(db_wishlist)
    db.commit()
    return True
