"""
Endpoints de Avaliações
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from ....core.database import get_db
from ....core.security import get_current_user
from ....models.usuario import Usuario
from ....schemas.avaliacao import AvaliacaoCreate, AvaliacaoResponse
from ....crud import avaliacao as crud_avaliacao
from ....crud import jogador as crud_jogador

router = APIRouter(prefix="/avaliacoes", tags=["Avaliações"])


@router.get("/jogador/{jogador_id}", response_model=List[AvaliacaoResponse])
def listar_avaliacoes_jogador(
    jogador_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Lista todas as avaliações de um jogador específico
    """
    # Verificar se jogador existe
    jogador = crud_jogador.get_jogador(db, jogador_id)
    if not jogador:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Jogador não encontrado"
        )

    avaliacoes = crud_avaliacao.get_avaliacoes_by_jogador(db, jogador_id, skip, limit)
    return [AvaliacaoResponse.model_validate(av) for av in avaliacoes]


@router.get("/jogador/{jogador_id}/ultima", response_model=AvaliacaoResponse)
def buscar_ultima_avaliacao(
    jogador_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Retorna a última avaliação de um jogador
    """
    avaliacao = crud_avaliacao.get_ultima_avaliacao(db, jogador_id)
    if not avaliacao:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nenhuma avaliação encontrada para este jogador"
        )
    return AvaliacaoResponse.model_validate(avaliacao)


@router.post("", response_model=AvaliacaoResponse, status_code=status.HTTP_201_CREATED)
def criar_avaliacao(
    avaliacao_data: AvaliacaoCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Cria nova avaliação para um jogador
    """
    # Verificar se jogador existe
    jogador = crud_jogador.get_jogador(db, avaliacao_data.id_jogador)
    if not jogador:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Jogador não encontrado"
        )

    avaliacao = crud_avaliacao.create_avaliacao(db, avaliacao_data)
    return AvaliacaoResponse.model_validate(avaliacao)


@router.delete("/{avaliacao_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_avaliacao(
    avaliacao_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Deleta uma avaliação
    """
    success = crud_avaliacao.delete_avaliacao(db, avaliacao_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Avaliação não encontrada"
        )
    return None
