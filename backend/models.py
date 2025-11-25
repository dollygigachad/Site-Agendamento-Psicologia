"""Modelos de dados da aplicação usando SQLModel."""
from datetime import datetime, timezone
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from pydantic import field_validator
from backend.enums import UserRole, AppointmentStatus


class Room(SQLModel, table=True):
    """
    Modelo de Sala de atendimento.
    
    Attributes:
        id: Identificador único
        name: Nome da sala (único)
        description: Descrição da sala
        capacity: Capacidade máxima de pessoas
        active: Indica se a sala está ativa
        created_at: Data de criação
        updated_at: Data da última atualização
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True, min_length=1, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    capacity: int = Field(default=1, ge=1, le=50)
    active: bool = Field(default=True, index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    appointments: List["Appointment"] = Relationship(back_populates="room")

    @field_validator("name")
    def name_must_not_be_empty(cls, v):
        """Valida se o nome não é apenas espaços em branco."""
        if not v or not v.strip():
            raise ValueError("Nome da sala não pode estar vazio")
        return v.strip()


class Patient(SQLModel, table=True):
    """
    Modelo de Paciente.
    
    Attributes:
        id: Identificador único
        name: Nome do paciente
        birthdate: Data de nascimento
        email: Email do paciente
        phone: Telefone do paciente
        is_child: Indica se é paciente infantojuvenil
        active: Indica se o paciente está ativo
        created_at: Data de criação
        updated_at: Data da última atualização
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, min_length=1, max_length=200)
    birthdate: Optional[datetime] = None
    email: Optional[str] = Field(default=None, max_length=100)
    phone: Optional[str] = Field(default=None, max_length=20)
    notes: Optional[str] = Field(default=None, max_length=1000)
    is_child: bool = Field(default=False)
    active: bool = Field(default=True, index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    appointments: List["Appointment"] = Relationship(back_populates="patient")

    @field_validator("name")
    def name_must_not_be_empty(cls, v):
        """Valida se o nome não é apenas espaços em branco."""
        if not v or not v.strip():
            raise ValueError("Nome do paciente não pode estar vazio")
        return v.strip()


class User(SQLModel, table=True):
    """
    Modelo de Usuário (estagiário, professor, admin).
    
    Attributes:
        id: Identificador único
        name: Nome do usuário
        email: Email único do usuário
        hashed_password: Senha criptografada
        role: Papel do usuário (admin, professor, student)
        is_active: Indica se o usuário está ativo
        created_at: Data de criação
        updated_at: Data da última atualização
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, min_length=1, max_length=200)
    email: str = Field(unique=True, index=True, max_length=100)
    hashed_password: str
    role: UserRole = Field(default=UserRole.STUDENT)
    is_active: bool = Field(default=True, index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("name")
    def name_must_not_be_empty(cls, v):
        """Valida se o nome não é apenas espaços em branco."""
        if not v or not v.strip():
            raise ValueError("Nome do usuário não pode estar vazio")
        return v.strip()

    @field_validator("email")
    def email_must_be_valid(cls, v):
        """Valida formato básico do email."""
        if not v or "@" not in v:
            raise ValueError("Email inválido")
        return v.lower().strip()


class Appointment(SQLModel, table=True):
    """
    Modelo de Agendamento.
    
    Attributes:
        id: Identificador único
        start_dt: Data/hora de início
        end_dt: Data/hora de fim
        status: Status do agendamento (scheduled, in_progress, completed, cancelled)
        notes: Notas sobre o agendamento
        is_deleted: Indica soft delete
        created_at: Data de criação
        updated_at: Data da última atualização
        room_id: ID da sala
        patient_id: ID do paciente
        student_id: ID do estagiário
        supervisor_id: ID do supervisor
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    start_dt: datetime = Field(index=True)
    end_dt: datetime = Field(index=True)
    status: AppointmentStatus = Field(default=AppointmentStatus.SCHEDULED, index=True)
    notes: Optional[str] = Field(default=None, max_length=1000)
    is_deleted: bool = Field(default=False, index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    room_id: Optional[int] = Field(default=None, foreign_key="room.id", index=True)
    patient_id: Optional[int] = Field(default=None, foreign_key="patient.id", index=True)
    student_id: Optional[int] = Field(default=None, foreign_key="user.id", index=True)
    supervisor_id: Optional[int] = Field(default=None, foreign_key="user.id", index=True)

    room: Optional[Room] = Relationship(back_populates="appointments")
    patient: Optional[Patient] = Relationship(back_populates="appointments")

    @field_validator("end_dt")
    def end_must_be_after_start(cls, v, values):
        """Valida que data de fim é posterior à data de início."""
        if "start_dt" in values and v <= values["start_dt"]:
            raise ValueError("Data de fim deve ser posterior à data de início")
        return v


