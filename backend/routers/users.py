"""Router para gerenciamento de usuÃ¡rios (estagiÃ¡rios, professores, admin)."""
from typing import List
from fastapi import APIRouter, HTTPException, status, Depends
from sqlmodel import Session, select
from ..models import User
from ..schemas import UserResponse, UserUpdate, UserCreate
from ..repository import UserRepository
from ..database import get_session
from ..logger import logger
from ..enums import UserRole
from ..security import hash_password

router = APIRouter(prefix="/api/users", tags=["users"])

# POST deve vir ANTES dos GETs para evitar colisÃ£o de rotas
@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user_data: UserCreate, session: Session = Depends(get_session)):
    """Cria novo usuÃ¡rio (equivalente a /api/auth/register)."""
    # Verificar se jÃ¡ existe
    existing = UserRepository.get_by_email(session, user_data.email)
    if existing:
        logger.warning(f"Tentativa de registrar email jÃ¡ existente: {user_data.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email jÃ¡ cadastrado"
        )
    
    # Criar novo usuÃ¡rio
    user = User(
        name=user_data.name,
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
        role=user_data.role
    )
    
    user = UserRepository.create(session, user)
    logger.info(f"Novo usuÃ¡rio registrado: {user.email} (role: {user.role})")
    return user

@router.get("", response_model=List[UserResponse])
def list_users(skip: int = 0, limit: int = 100, session: Session = Depends(get_session)):
    """Lista todos os usuÃ¡rios."""
    users = UserRepository.get_active_users(session)
    return users[skip : skip + limit]

@router.get("/students", response_model=List[UserResponse])
def list_students(session: Session = Depends(get_session)):
    """Lista todos os estagiÃ¡rios."""
    stmt = select(User).where(
        (User.role == UserRole.STUDENT) & (User.is_active == True)
    )
    students = session.exec(stmt).all()
    return students

@router.get("/professors", response_model=List[UserResponse])
def list_professors(session: Session = Depends(get_session)):
    """Lista todos os professores supervisores."""
    stmt = select(User).where(
        (User.role == UserRole.PROFESSOR) & (User.is_active == True)
    )
    professors = session.exec(stmt).all()
    return professors

@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, session: Session = Depends(get_session)):
    """ObtÃ©m usuÃ¡rio por ID."""
    user = session.get(User, user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=404, detail="UsuÃ¡rio nÃ£o encontrado")
    return user

@router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user_data: UserUpdate, session: Session = Depends(get_session)):
    """Atualiza usuÃ¡rio."""
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="UsuÃ¡rio nÃ£o encontrado")
    
    user = UserRepository.update(session, user_id, user_data.dict(exclude_unset=True))
    logger.info(f"UsuÃ¡rio atualizado: {user.email}")
    return user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, session: Session = Depends(get_session)):
    """Deleta usuÃ¡rio (soft delete)."""
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="UsuÃ¡rio nÃ£o encontrado")
    
    UserRepository.update(session, user_id, {"is_active": False})
    logger.info(f"UsuÃ¡rio desativado: {user.email}")




