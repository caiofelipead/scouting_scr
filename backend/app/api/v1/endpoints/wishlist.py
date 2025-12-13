"""
Endpoints de Wishlist
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from ....core.database import get_db
from ....core.security import get_current_user
from ....models.usuario import Usuario
from ....schemas.wishlist import WishlistCreate, WishlistResponse
from ....crud import wishlist as crud_wishlist
from ....crud import jogador as crud_jogador

router = APIRouter(prefix="/wishlist", tags=["Wishlist"])


@router.get("", response_model=List[WishlistResponse])
def listar_wishlist(
    prioridade: Optional[str] = Query(None, regex="^(alta|media|baixa)$"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Lista jogadores na wishlist com filtro opcional por prioridade
    """
    wishlist_items = crud_wishlist.get_wishlist(db, prioridade, skip, limit)
    return [WishlistResponse.model_validate(item) for item in wishlist_items]


@router.post("", response_model=WishlistResponse, status_code=status.HTTP_201_CREATED)
def adicionar_wishlist(
    wishlist_data: WishlistCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Adiciona jogador à wishlist
    """
    # Verificar se jogador existe
    jogador = crud_jogador.get_jogador(db, wishlist_data.id_jogador)
    if not jogador:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Jogador não encontrado"
        )

    # Verificar se já está na wishlist
    existing = crud_wishlist.get_wishlist_by_jogador(db, wishlist_data.id_jogador)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Jogador já está na wishlist"
        )

    wishlist_item = crud_wishlist.create_wishlist_item(db, wishlist_data)
    return WishlistResponse.model_validate(wishlist_item)


@router.delete("/{jogador_id}", status_code=status.HTTP_204_NO_CONTENT)
def remover_wishlist(
    jogador_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Remove jogador da wishlist
    """
    success = crud_wishlist.delete_wishlist_item(db, jogador_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Jogador não está na wishlist"
        )
    return None


@router.get("/check/{jogador_id}", response_model=dict)
def verificar_wishlist(
    jogador_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Verifica se um jogador está na wishlist
    """
    item = crud_wishlist.get_wishlist_by_jogador(db, jogador_id)
    return {
        "em_wishlist": item is not None,
        "prioridade": item.prioridade if item else None
    }
