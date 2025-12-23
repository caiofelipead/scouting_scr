"""
API Endpoints - Statistics & Dashboard
KPIs, analytics, and system monitoring
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from datetime import datetime, timedelta

from app.api import deps
from app.core.database import get_database

router = APIRouter()


@router.get("/dashboard")
async def get_dashboard_stats(
    db: Session = Depends(get_database),
    current_user = Depends(deps.get_current_active_user),
) -> Dict[str, Any]:
    """
    Get main dashboard statistics and KPIs
    """
    # TODO: Implement actual database queries
    # For now, return simulated data

    return {
        "total_jogadores": 707,
        "crescimento_semanal": 3.2,  # 3.2% growth
        "media_geral": 3.8,
        "meta_clube": 4.0,
        "alertas_contrato": 42,
        "wishlist_ativa": 28,
        "distribuicao_posicao": [
            {"posicao": "GOL", "count": 32},
            {"posicao": "ZAG", "count": 98},
            {"posicao": "LE", "count": 45},
            {"posicao": "LD", "count": 48},
            {"posicao": "VOL", "count": 67},
            {"posicao": "MC", "count": 112},
            {"posicao": "MA", "count": 89},
            {"posicao": "AE", "count": 67},
            {"posicao": "AD", "count": 71},
            {"posicao": "ATA", "count": 78},
        ],
    }


@router.get("/top-prospects")
async def get_top_prospects(
    limit: int = 5,
    db: Session = Depends(get_database),
    current_user = Depends(deps.get_current_active_user),
) -> List[Dict[str, Any]]:
    """
    Get top prospects (U23 with highest average)
    """
    # TODO: Implement actual database query
    # SELECT * FROM jogadores WHERE idade_atual < 23 ORDER BY nota_media DESC LIMIT 5

    return [
        {
            "id_jogador": 123,
            "nome": "Endrick Felipe",
            "idade_atual": 17,
            "posicao": "ATA",
            "clube": "Real Madrid",
            "media_geral": 4.7,
            "transfermarkt_id": 846653,
        },
        {
            "id_jogador": 124,
            "nome": "Estêvão Willian",
            "idade_atual": 17,
            "posicao": "AE",
            "clube": "Palmeiras",
            "media_geral": 4.6,
            "transfermarkt_id": 912345,
        },
        {
            "id_jogador": 125,
            "nome": "Vitor Roque",
            "idade_atual": 19,
            "posicao": "ATA",
            "clube": "Barcelona",
            "media_geral": 4.5,
            "transfermarkt_id": 798362,
        },
        {
            "id_jogador": 126,
            "nome": "João Neves",
            "idade_atual": 19,
            "posicao": "MC",
            "clube": "Benfica",
            "media_geral": 4.4,
            "transfermarkt_id": 801234,
        },
        {
            "id_jogador": 127,
            "nome": "Leny Yoro",
            "idade_atual": 18,
            "posicao": "ZAG",
            "clube": "Lille",
            "media_geral": 4.3,
            "transfermarkt_id": 789456,
        },
    ][:limit]


@router.get("/activity-feed")
async def get_activity_feed(
    limit: int = 5,
    db: Session = Depends(get_database),
    current_user = Depends(deps.get_current_active_user),
) -> List[Dict[str, Any]]:
    """
    Get recent activity feed (evaluations, new players, etc.)
    """
    # TODO: Implement actual database query

    return [
        {
            "id": 1,
            "tipo": "avaliacao",
            "descricao": "Nova avaliação para Neymar Jr.",
            "usuario": "João Silva",
            "created_at": (datetime.utcnow() - timedelta(hours=2)).isoformat(),
            "metadata": {"jogador_id": 100, "nota_geral": 4.5},
        },
        {
            "id": 2,
            "tipo": "jogador_novo",
            "descricao": "Jogador adicionado via scraping: Endrick Felipe",
            "usuario": "Sistema",
            "created_at": (datetime.utcnow() - timedelta(hours=5)).isoformat(),
            "metadata": {"jogador_id": 123},
        },
        {
            "id": 3,
            "tipo": "wishlist_add",
            "descricao": "Vitor Roque adicionado à wishlist (Alta prioridade)",
            "usuario": "Maria Santos",
            "created_at": (datetime.utcnow() - timedelta(hours=8)).isoformat(),
            "metadata": {"jogador_id": 125, "prioridade": "Alta"},
        },
        {
            "id": 4,
            "tipo": "avaliacao",
            "descricao": "Nova avaliação para Vinicius Jr.",
            "usuario": "Pedro Costa",
            "created_at": (datetime.utcnow() - timedelta(days=1)).isoformat(),
            "metadata": {"jogador_id": 101, "nota_geral": 4.8},
        },
        {
            "id": 5,
            "tipo": "jogador_novo",
            "descricao": "Jogador adicionado: Leny Yoro",
            "usuario": "João Silva",
            "created_at": (datetime.utcnow() - timedelta(days=2)).isoformat(),
            "metadata": {"jogador_id": 127},
        },
    ][:limit]


@router.get("/system-status")
async def get_system_status(
    db: Session = Depends(get_database),
    current_user = Depends(deps.get_current_active_user),
) -> Dict[str, Any]:
    """
    Get system status (API connections, last sync, etc.)
    """
    # TODO: Implement actual health checks

    return {
        "api_transfermarkt": "online",
        "google_sheets": "online",
        "database": "online",
        "ultimo_sync": (datetime.utcnow() - timedelta(hours=3)).isoformat(),
    }
