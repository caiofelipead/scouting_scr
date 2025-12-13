"""
Endpoints de Jogadores
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from ....core.database import get_db
from ....core.security import get_current_user
from ....models.usuario import Usuario
from ....schemas.jogador import (
    JogadorCreate,
    JogadorUpdate,
    JogadorResponse,
    JogadorWithDetails
)
from ....crud import jogador as crud_jogador

router = APIRouter(prefix="/jogadores", tags=["Jogadores"])


@router.get("", response_model=List[JogadorWithDetails])
def listar_jogadores(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    nome: Optional[str] = Query(None, description="Filtrar por nome"),
    nacionalidade: Optional[str] = Query(None, description="Filtrar por nacionalidade"),
    clube: Optional[str] = Query(None, description="Filtrar por clube"),
    posicao: Optional[str] = Query(None, description="Filtrar por posição"),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Lista todos os jogadores com filtros opcionais.
    Retorna dados agregados (última avaliação, vínculo atual, wishlist).
    """
    jogadores_data = crud_jogador.get_jogadores_com_detalhes(db, skip=skip, limit=limit)

    # Transformar em JogadorWithDetails
    result = []
    for row in jogadores_data:
        jogador = row[0]  # Objeto Jogador
        data = {
            **jogador.__dict__,
            "clube": row[1],
            "liga_clube": row[2],
            "posicao": row[3],
            "status_contrato": row[4],
            "data_fim_contrato": row[5],
            "nota_potencial_media": float(row[6]) if row[6] else None,
            "total_avaliacoes": row[7] or 0,
            "em_wishlist": bool(row[8])
        }
        result.append(JogadorWithDetails(**data))

    return result


@router.get("/{jogador_id}", response_model=JogadorResponse)
def buscar_jogador(
    jogador_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Busca jogador por ID
    """
    jogador = crud_jogador.get_jogador(db, jogador_id)
    if not jogador:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Jogador não encontrado"
        )
    return JogadorResponse.model_validate(jogador)


@router.post("", response_model=JogadorResponse, status_code=status.HTTP_201_CREATED)
def criar_jogador(
    jogador_data: JogadorCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Cria novo jogador
    """
    # Verificar se Transfermarkt ID já existe
    if jogador_data.transfermarkt_id:
        existing = crud_jogador.get_jogador_by_tm_id(db, jogador_data.transfermarkt_id)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Jogador com este Transfermarkt ID já existe"
            )

    jogador = crud_jogador.create_jogador(db, jogador_data)
    return JogadorResponse.model_validate(jogador)


@router.put("/{jogador_id}", response_model=JogadorResponse)
def atualizar_jogador(
    jogador_id: int,
    jogador_data: JogadorUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Atualiza jogador existente
    """
    jogador = crud_jogador.update_jogador(db, jogador_id, jogador_data)
    if not jogador:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Jogador não encontrado"
        )
    return JogadorResponse.model_validate(jogador)


@router.delete("/{jogador_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_jogador(
    jogador_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Deleta jogador (requer autenticação)
    """
    success = crud_jogador.delete_jogador(db, jogador_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Jogador não encontrado"
        )
    return None


@router.get("/stats/total", response_model=dict)
def estatisticas_jogadores(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Retorna estatísticas gerais dos jogadores
    """
    total = crud_jogador.count_jogadores(db)
    return {"total_jogadores": total}
