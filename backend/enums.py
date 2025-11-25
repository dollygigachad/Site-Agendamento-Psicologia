"""Enumerações e funções auxiliares de tempo."""
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    """Papéis de usuário no sistema."""
    ADMIN = "admin"
    PROFESSOR = "professor"
    STUDENT = "student"
    PATIENT = "patient"


class AppointmentStatus(str, Enum):
    """Status de um agendamento."""
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"


def time_overlaps(start1: datetime, end1: datetime, start2: datetime, end2: datetime) -> bool:
    """
    Verifica se dois períodos de tempo se sobrepõem.
    
    Args:
        start1: Início do primeiro período
        end1: Fim do primeiro período
        start2: Início do segundo período
        end2: Fim do segundo período
    
    Returns:
        True se os períodos se sobrepõem, False caso contrário
    """
    return start1 < end2 and end1 > start2


def get_day_start(dt: datetime) -> datetime:
    """
    Retorna o início do dia (00:00:00).
    
    Args:
        dt: Data/hora de referência
    
    Returns:
        Data com hora marcada como início do dia
    """
    return dt.replace(hour=0, minute=0, second=0, microsecond=0)


def get_day_end(dt: datetime) -> datetime:
    """
    Retorna o fim do dia (23:59:59).
    
    Args:
        dt: Data/hora de referência
    
    Returns:
        Data com hora marcada como fim do dia
    """
    return dt.replace(hour=23, minute=59, second=59, microsecond=999999)


def minutes_between(start: datetime, end: datetime) -> float:
    """
    Retorna a quantidade de minutos entre dois datetimes.
    
    Args:
        start: Data/hora inicial
        end: Data/hora final
    
    Returns:
        Número de minutos entre os dois datetimes
    
    Raises:
        ValueError: Se start for posterior a end
    """
    if start > end:
        raise ValueError("Data inicial deve ser anterior à data final")
    return (end - start).total_seconds() / 60


def hours_between(start: datetime, end: datetime) -> float:
    """
    Retorna a quantidade de horas entre dois datetimes.
    
    Args:
        start: Data/hora inicial
        end: Data/hora final
    
    Returns:
        Número de horas entre os dois datetimes
    """
    return minutes_between(start, end) / 60

