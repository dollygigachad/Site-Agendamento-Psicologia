# Pacote backend - expõe módulos principais
from backend.models import Room, Patient, User, Appointment
from backend.enums import UserRole, AppointmentStatus
from backend.config import get_settings, Settings
from backend.database import create_db_and_tables, get_session, get_session_context
from backend.logger import logger

__all__ = [
    "Room", "Patient", "User", "Appointment",
    "UserRole", "AppointmentStatus",
    "get_settings", "Settings",
    "create_db_and_tables", "get_session", "get_session_context",
    "logger"
]

