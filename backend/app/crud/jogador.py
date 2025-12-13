"""
CRUD Operations para Jogador
"""
from typing import Optional, List
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, desc

from ..models.jogador import Jogador
from ..models.vinculo import VinculoClube
from ..models.avaliacao import Avaliacao
from ..models.wishlist import Wishlist
from ..schemas.jogador import JogadorCreate, JogadorUpdate


def get_jogador(db: Session, jogador_id: int) -> Optional[Jogador]:
    """Busca jogador por ID"""
    return db.query(Jogador).filter(Jogador.id_jogador == jogador_id).first()


def get_jogador_by_tm_id(db: Session, tm_id: str) -> Optional[Jogador]:
    """Busca jogador por Transfermarkt ID"""
    return db.query(Jogador).filter(Jogador.transfermarkt_id == tm_id).first()


def get_jogadores(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    nome: Optional[str] = None,
    nacionalidade: Optional[str] = None,
    clube: Optional[str] = None,
    posicao: Optional[str] = None,
) -> List[Jogador]:
    """
    Lista jogadores com filtros opcionais e paginação.
    Carrega relacionamentos (vinculos, avaliacoes) com joinedload.
    """
    query = db.query(Jogador).options(
        joinedload(Jogador.vinculos),
        joinedload(Jogador.avaliacoes),
        joinedload(Jogador.wishlist)
    )

    # Filtros
    if nome:
        query = query.filter(Jogador.nome.ilike(f"%{nome}%"))
    if nacionalidade:
        query = query.filter(Jogador.nacionalidade.ilike(f"%{nacionalidade}%"))

    # Filtros por vínculo (JOIN)
    if clube or posicao:
        query = query.join(VinculoClube)
        if clube:
            query = query.filter(VinculoClube.clube.ilike(f"%{clube}%"))
        if posicao:
            query = query.filter(VinculoClube.posicao.ilike(f"%{posicao}%"))

    return query.order_by(Jogador.nome).offset(skip).limit(limit).all()


def get_jogadores_com_detalhes(db: Session, skip: int = 0, limit: int = 100):
    """
    Retorna jogadores com informações agregadas (última avaliação, vínculo atual)
    Otimizado para evitar N+1 queries
    """
    subquery_avaliacao = (
        db.query(
            Avaliacao.id_jogador,
            func.avg(Avaliacao.nota_potencial).label("nota_potencial_media"),
            func.count(Avaliacao.id).label("total_avaliacoes")
        )
        .group_by(Avaliacao.id_jogador)
        .subquery()
    )

    query = (
        db.query(
            Jogador,
            VinculoClube.clube,
            VinculoClube.liga_clube,
            VinculoClube.posicao,
            VinculoClube.status_contrato,
            VinculoClube.data_fim_contrato,
            subquery_avaliacao.c.nota_potencial_media,
            subquery_avaliacao.c.total_avaliacoes,
            Wishlist.id.isnot(None).label("em_wishlist")
        )
        .outerjoin(VinculoClube, Jogador.id_jogador == VinculoClube.id_jogador)
        .outerjoin(subquery_avaliacao, Jogador.id_jogador == subquery_avaliacao.c.id_jogador)
        .outerjoin(Wishlist, Jogador.id_jogador == Wishlist.id_jogador)
        .order_by(Jogador.nome)
        .offset(skip)
        .limit(limit)
    )

    return query.all()


def create_jogador(db: Session, jogador: JogadorCreate) -> Jogador:
    """Cria novo jogador"""
    db_jogador = Jogador(**jogador.model_dump())
    db.add(db_jogador)
    db.commit()
    db.refresh(db_jogador)
    return db_jogador


def update_jogador(db: Session, jogador_id: int, jogador_update: JogadorUpdate) -> Optional[Jogador]:
    """Atualiza jogador existente"""
    db_jogador = get_jogador(db, jogador_id)
    if not db_jogador:
        return None

    # Atualiza apenas campos fornecidos (exclude_unset=True)
    update_data = jogador_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_jogador, field, value)

    db.commit()
    db.refresh(db_jogador)
    return db_jogador


def delete_jogador(db: Session, jogador_id: int) -> bool:
    """Deleta jogador (cascade deleta relacionamentos)"""
    db_jogador = get_jogador(db, jogador_id)
    if not db_jogador:
        return False

    db.delete(db_jogador)
    db.commit()
    return True


def count_jogadores(db: Session) -> int:
    """Conta total de jogadores"""
    return db.query(func.count(Jogador.id_jogador)).scalar()
