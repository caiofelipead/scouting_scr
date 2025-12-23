"""
Dependencies para injeção em endpoints FastAPI
"""
from typing import Generator, Optional
from fastapi import Depends, HTTPException, status, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..core.security import decode_token, get_current_user
from ..core.config import settings
from ..models.usuario import Usuario


# Security scheme para Swagger UI
security = HTTPBearer()


# ============================================
# DATABASE DEPENDENCY
# ============================================

def get_database() -> Generator[Session, None, None]:
    """
    Dependency que fornece sessão do banco de dados.

    Uso:
        @router.get("/items")
        def read_items(db: Session = Depends(get_database)):
            ...
    """
    return get_db()


# ============================================
# AUTENTICAÇÃO
# ============================================

async def get_current_active_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_database)
) -> Usuario:
    """
    Dependency que retorna o usuário autenticado e ativo.

    Validações:
    - Token JWT válido
    - Usuário existe no banco
    - Usuário está ativo

    Raises:
        HTTPException 401: Token inválido ou expirado
        HTTPException 403: Usuário inativo

    Uso:
        @router.get("/protected")
        def protected_route(current_user: Usuario = Depends(get_current_active_user)):
            return {"user": current_user.username}
    """
    return await get_current_user(credentials, db)


async def get_current_admin_user(
    current_user: Usuario = Depends(get_current_active_user)
) -> Usuario:
    """
    Dependency que verifica se o usuário é admin.

    Raises:
        HTTPException 403: Usuário não é admin

    Uso:
        @router.post("/admin-only")
        def admin_route(current_user: Usuario = Depends(get_current_admin_user)):
            ...
    """
    if current_user.nivel != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissão insuficiente. Apenas administradores.",
        )
    return current_user


async def get_current_coordenador_or_admin(
    current_user: Usuario = Depends(get_current_active_user)
) -> Usuario:
    """
    Dependency que verifica se o usuário é coordenador ou admin.

    Raises:
        HTTPException 403: Usuário não tem permissão

    Uso:
        @router.post("/coordenador-route")
        def route(current_user: Usuario = Depends(get_current_coordenador_or_admin)):
            ...
    """
    if current_user.nivel not in ["admin", "coordenador"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissão insuficiente. Apenas administradores e coordenadores.",
        )
    return current_user


# ============================================
# PAGINAÇÃO
# ============================================

class PaginationParams:
    """
    Dependency para parâmetros de paginação.

    Query params:
    - page: Número da página (1-indexed)
    - limit: Número de items por página

    Uso:
        @router.get("/items")
        def list_items(pagination: PaginationParams = Depends()):
            skip = (pagination.page - 1) * pagination.limit
            limit = pagination.limit
    """

    def __init__(
        self,
        page: int = Query(1, ge=1, description="Número da página (1-indexed)"),
        limit: int = Query(
            settings.DEFAULT_PAGE_SIZE,
            ge=1,
            le=settings.MAX_PAGE_SIZE,
            description=f"Items por página (máx: {settings.MAX_PAGE_SIZE})"
        )
    ):
        self.page = page
        self.limit = limit
        self.skip = (page - 1) * limit


# ============================================
# FILTROS
# ============================================

class JogadorFilterParams:
    """
    Dependency para filtros de jogadores.

    Query params:
    - nome: Busca por nome (case-insensitive)
    - posicao: Filtro por posição
    - clube: Filtro por clube
    - liga: Filtro por liga
    - nacionalidade: Filtro por nacionalidade
    - idade_min/idade_max: Filtro por faixa etária
    - media_min: Filtro por média mínima

    Uso:
        @router.get("/jogadores")
        def list_jogadores(filters: JogadorFilterParams = Depends()):
            ...
    """

    def __init__(
        self,
        nome: Optional[str] = Query(None, description="Busca por nome"),
        posicao: Optional[str] = Query(None, description="Filtro por posição (ex: ATA, MEI)"),
        clube: Optional[str] = Query(None, description="Filtro por clube"),
        liga: Optional[str] = Query(None, description="Filtro por liga"),
        nacionalidade: Optional[str] = Query(None, description="Filtro por nacionalidade"),
        idade_min: Optional[int] = Query(None, ge=14, le=50, description="Idade mínima"),
        idade_max: Optional[int] = Query(None, ge=14, le=50, description="Idade máxima"),
        media_min: Optional[float] = Query(None, ge=0.0, le=5.0, description="Média geral mínima"),
    ):
        self.nome = nome
        self.posicao = posicao
        self.clube = clube
        self.liga = liga
        self.nacionalidade = nacionalidade
        self.idade_min = idade_min
        self.idade_max = idade_max
        self.media_min = media_min


# ============================================
# VALIDAÇÕES
# ============================================

def validate_jogador_exists(
    jogador_id: int,
    db: Session = Depends(get_database)
):
    """
    Dependency que valida se um jogador existe.

    Raises:
        HTTPException 404: Jogador não encontrado

    Uso:
        @router.get("/jogadores/{jogador_id}")
        def get_jogador(
            jogador: Jogador = Depends(validate_jogador_exists)
        ):
            return jogador
    """
    from ..crud.jogador import get_jogador

    jogador = get_jogador(db, jogador_id)
    if not jogador:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Jogador com ID {jogador_id} não encontrado"
        )
    return jogador


# ============================================
# RATE LIMITING (Opcional - para implementar)
# ============================================

# TODO: Implementar rate limiting com Redis
# from slowapi import Limiter
# from slowapi.util import get_remote_address
# limiter = Limiter(key_func=get_remote_address)
