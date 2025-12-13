"""
Endpoints de Autenticação
"""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ....core.database import get_db
from ....core.security import (
    authenticate_user,
    create_access_token,
    create_refresh_token,
    hash_password,
    get_current_user
)
from ....models.usuario import Usuario
from ....schemas.usuario import LoginRequest, Token, UsuarioCreate, UsuarioResponse

router = APIRouter(prefix="/auth", tags=["Autenticação"])


@router.post("/login", response_model=Token)
def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    """
    Login - Autentica usuário e retorna tokens JWT
    """
    usuario = authenticate_user(db, credentials.username, credentials.password)

    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Atualizar último acesso
    usuario.ultimo_acesso = datetime.utcnow()
    db.commit()

    # Criar tokens
    token_data = {
        "sub": usuario.id,
        "username": usuario.username,
        "nivel": usuario.nivel
    }
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        usuario=UsuarioResponse.model_validate(usuario)
    )


@router.post("/register", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
def register(usuario_data: UsuarioCreate, db: Session = Depends(get_db)):
    """
    Registra novo usuário
    """
    # Verificar se username já existe
    existing_user = db.query(Usuario).filter(Usuario.username == usuario_data.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username já cadastrado"
        )

    # Verificar se email já existe
    existing_email = db.query(Usuario).filter(Usuario.email == usuario_data.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email já cadastrado"
        )

    # Criar usuário
    senha_hash = hash_password(usuario_data.password)
    db_usuario = Usuario(
        username=usuario_data.username,
        email=usuario_data.email,
        nome=usuario_data.nome,
        nivel=usuario_data.nivel,
        senha_hash=senha_hash
    )

    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)

    return UsuarioResponse.model_validate(db_usuario)


@router.get("/me", response_model=UsuarioResponse)
async def get_current_user_info(current_user: Usuario = Depends(get_current_user)):
    """
    Retorna informações do usuário autenticado
    """
    return UsuarioResponse.model_validate(current_user)
