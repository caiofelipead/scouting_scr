"""
Scout Pro API - Backend FastAPI
Sistema de Scouting de Jogadores de Futebol
"""
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from .core.config import settings
from .core.database import engine, Base
from .api.v1.endpoints import auth, jogadores, avaliacoes, wishlist


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifecycle events - Executado na inicialização e shutdown da aplicação
    """
    # Startup
    print("🚀 Iniciando Scout Pro API...")
    print(f"📊 Conectando ao banco de dados: {settings.DATABASE_URL.split('@')[1]}")

    # Criar tabelas (se não existirem)
    # NOTA: Em produção, usar Alembic para migrations
    # Base.metadata.create_all(bind=engine)

    yield

    # Shutdown
    print("👋 Encerrando Scout Pro API...")
    engine.dispose()


# Criar aplicação FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="API REST para Sistema de Scouting de Jogadores de Futebol",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan
)


# ============================================
# MIDDLEWARE - CORS
# ============================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,  # React frontend
    allow_credentials=True,
    allow_methods=["*"],  # GET, POST, PUT, DELETE, etc.
    allow_headers=["*"],  # Authorization, Content-Type, etc.
)


# ============================================
# ROUTERS - Endpoints
# ============================================

# Autenticação
app.include_router(auth.router, prefix="/api/v1")

# Jogadores
app.include_router(jogadores.router, prefix="/api/v1")

# Avaliações
app.include_router(avaliacoes.router, prefix="/api/v1")

# Wishlist
app.include_router(wishlist.router, prefix="/api/v1")


# ============================================
# ENDPOINTS RAIZ
# ============================================

@app.get("/", tags=["Health"])
def root():
    """Endpoint raiz - Health check"""
    return {
        "message": "Scout Pro API",
        "version": settings.APP_VERSION,
        "status": "online",
        "docs": "/api/docs"
    }


@app.get("/api/health", tags=["Health"])
def health_check():
    """Health check detalhado"""
    return {
        "status": "healthy",
        "database": "connected",
        "version": settings.APP_VERSION
    }


# ============================================
# EXCEPTION HANDLERS
# ============================================

@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Handler customizado para 404"""
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": "Recurso não encontrado"}
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Handler customizado para 500"""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Erro interno do servidor"}
    )


# ============================================
# EXECUÇÃO LOCAL (desenvolvimento)
# ============================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Hot reload em desenvolvimento
        log_level="info"
    )
