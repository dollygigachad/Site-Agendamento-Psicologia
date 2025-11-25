"""Router para gerenciamento de salas."""
from typing import List
from fastapi import APIRouter, HTTPException, status, Depends
from sqlmodel import Session
from ..models import Room
from ..schemas import RoomCreate, RoomUpdate, RoomResponse
from ..repository import RoomRepository
from ..database import get_session
from ..logger import logger

router = APIRouter(prefix="/api/rooms", tags=["rooms"])

@router.get("", response_model=List[RoomResponse])
def list_rooms(skip: int = 0, limit: int = 100, session: Session = Depends(get_session)):
    """Lista todas as salas."""
    rooms = RoomRepository.get_active_rooms(session)
    return rooms[skip : skip + limit]

@router.get("/{room_id}", response_model=RoomResponse)
def get_room(room_id: int, session: Session = Depends(get_session)):
    """Obtém sala por ID."""
    room = session.get(Room, room_id)
    if not room or not room.active:
        raise HTTPException(status_code=404, detail="Sala não encontrada")
    return room

@router.post("", response_model=RoomResponse, status_code=status.HTTP_201_CREATED)
def create_room(room_data: RoomCreate, session: Session = Depends(get_session)):
    """Cria nova sala."""
    existing = RoomRepository.get_by_name(session, room_data.name)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Sala com este nome já existe"
        )
    
    room = Room(**room_data.model_dump())
    room = RoomRepository.create(session, room)
    logger.info(f"Nova sala criada: {room.name}")
    return room

@router.put("/{room_id}", response_model=RoomResponse)
def update_room(room_id: int, room_data: RoomUpdate, session: Session = Depends(get_session)):
    """Atualiza sala."""
    room = session.get(Room, room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Sala não encontrada")
    
    room = RoomRepository.update(session, room_id, room_data.model_dump(exclude_unset=True))
    logger.info(f"Sala atualizada: {room.name}")
    return room

@router.delete("/{room_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_room(room_id: int, session: Session = Depends(get_session)):
    """Deleta sala (soft delete)."""
    room = session.get(Room, room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Sala não encontrada")
    
    RoomRepository.update(session, room_id, {"active": False})
    logger.info(f"Sala desativada: {room.name}")




