"""Funções utilitárias da aplicação."""
from sqlmodel import Session, select
from datetime import datetime
from typing import Optional, List
from backend.models import Appointment
from backend.enums import AppointmentStatus


def has_conflict(
    session: Session,
    start_dt: datetime,
    end_dt: datetime,
    room_id: Optional[int] = None,
    student_id: Optional[int] = None,
    supervisor_id: Optional[int] = None
) -> bool:
    """
    Verifica se há conflito de agendamento.
    
    Retorna True se há um agendamento conflitante para sala, estagiário ou supervisor.
    
    Args:
        session: Sessão do banco de dados
        start_dt: Data/hora de início
        end_dt: Data/hora de fim
        room_id: ID da sala (opcional)
        student_id: ID do estagiário (opcional)
        supervisor_id: ID do supervisor (opcional)
    
    Returns:
        True se há conflito, False caso contrário
    """
    stmt = select(Appointment).where(
        (Appointment.start_dt < end_dt)
        & (Appointment.end_dt > start_dt)
        & (Appointment.is_deleted == False)
        & (Appointment.status != AppointmentStatus.CANCELLED)
    )
    results = session.exec(stmt).all()
    
    for ap in results:
        if room_id and ap.room_id == room_id:
            return True
        if student_id and ap.student_id == student_id:
            return True
        if supervisor_id and ap.supervisor_id == supervisor_id:
            return True
    
    return False


def format_time_duration(minutes: float) -> str:
    """
    Formata duração em minutos para formato legível (ex: "1h 30min").
    
    Args:
        minutes: Quantidade de minutos
    
    Returns:
        String formatada com horas e minutos
    """
    hours = int(minutes // 60)
    remaining_minutes = int(minutes % 60)
    
    if hours == 0:
        return f"{remaining_minutes}min"
    elif remaining_minutes == 0:
        return f"{hours}h"
    else:
        return f"{hours}h {remaining_minutes}min"


def is_valid_email(email: str) -> bool:
    """
    Valida formato básico de email.
    
    Args:
        email: String com email a validar
    
    Returns:
        True se formato é válido
    """
    return "@" in email and "." in email.split("@")[-1]


def sanitize_string(text: str) -> str:
    """
    Remove espaços em branco desnecessários de uma string.
    
    Args:
        text: Texto a sanitizar
    
    Returns:
        Texto sanitizado
    """
    return text.strip() if text else ""


def paginate(items: List, skip: int = 0, limit: int = 100) -> List:
    """
    Pagina uma lista de itens.
    
    Args:
        items: Lista de itens
        skip: Número de itens a pular
        limit: Número máximo de itens a retornar
    
    Returns:
        Lista paginada
    """
    return items[skip : skip + limit]

