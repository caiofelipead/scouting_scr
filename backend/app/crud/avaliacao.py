"""
CRUD Operations para Avaliacao
"""
from typing import Optional, List
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import desc

from ..models.avaliacao import Avaliacao
from ..schemas.avaliacao import AvaliacaoCreate


def get_avaliacao(db: Session, avaliacao_id: int) -> Optional[Avaliacao]:
    """Busca avaliação por ID"""
    return db.query(Avaliacao).filter(Avaliacao.id == avaliacao_id).first()


def get_avaliacoes_by_jogador(
    db: Session,
    jogador_id: int,
    skip: int = 0,
    limit: int = 50
) -> List[Avaliacao]:
    """Lista avaliações de um jogador (ordenadas por data)"""
    return (
        db.query(Avaliacao)
        .filter(Avaliacao.id_jogador == jogador_id)
        .order_by(desc(Avaliacao.data_avaliacao))
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_ultima_avaliacao(db: Session, jogador_id: int) -> Optional[Avaliacao]:
    """Retorna última avaliação de um jogador"""
    return (
        db.query(Avaliacao)
        .filter(Avaliacao.id_jogador == jogador_id)
        .order_by(desc(Avaliacao.data_avaliacao))
        .first()
    )


def create_avaliacao(db: Session, avaliacao: AvaliacaoCreate) -> Avaliacao:
    """Cria nova avaliação"""
    db_avaliacao = Avaliacao(**avaliacao.model_dump())
    db.add(db_avaliacao)
    db.commit()
    db.refresh(db_avaliacao)
    return db_avaliacao


def delete_avaliacao(db: Session, avaliacao_id: int) -> bool:
    """Deleta avaliação"""
    db_avaliacao = get_avaliacao(db, avaliacao_id)
    if not db_avaliacao:
        return False

    db.delete(db_avaliacao)
    db.commit()
    return True
