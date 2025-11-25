"""Router para autenticação."""
from datetime import timedelta
from fastapi import APIRouter, HTTPException, status, Depends
from sqlmodel import Session
from ..models import User
from ..schemas import TokenResponse, LoginRequest, UserCreate, UserResponse
from ..security import (
    create_access_token,
    verify_password,
    hash_password,
    get_settings
)
from ..repository import UserRepository
from ..database import get_session
from ..logger import logger

router = APIRouter(prefix="/api/auth", tags=["auth"])
settings = get_settings()

@router.post("/register", response_model=UserResponse)
def register(user_data: UserCreate, session: Session = Depends(get_session)):
    """Registra novo usuário."""
    # Verificar se já existe
    existing = UserRepository.get_by_email(session, user_data.email)
    if existing:
        logger.warning(f"Tentativa de registrar email já existente: {user_data.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email já cadastrado"
        )
    
    # Criar novo usuário
    user = User(
        name=user_data.name,
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
        role=user_data.role
    )
    
    user = UserRepository.create(session, user)
    logger.info(f"Novo usuário registrado: {user.email} (role: {user.role})")
    return user

@router.post("/login", response_model=TokenResponse)
def login(credentials: LoginRequest, session: Session = Depends(get_session)):
    """Login e geração de JWT token."""
    user = UserRepository.get_by_email(session, credentials.email)
    
    if not user or not verify_password(credentials.password, user.hashed_password):
        logger.warning(f"Tentativa de login com credenciais inválidas: {credentials.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos"
        )
    
    if not user.is_active:
        logger.warning(f"Tentativa de login com usuário inativo: {credentials.email}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário inativo"
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=access_token_expires
    )
    
    logger.info(f"Login bem-sucedido: {user.email}")
    return {"access_token": access_token, "token_type": "bearer"}




