"""Camada de repositório - acesso a dados."""
from datetime import datetime, timezone
from typing import List, Optional, TypeVar, Generic, Type
from sqlmodel import Session, select
from backend.models import Room, Patient, User, Appointment
from backend.enums import AppointmentStatus
from .logger import logger

T = TypeVar('T')


class BaseRepository(Generic[T]):
    """Classe base genérica para repositórios."""
    model: Type[T] = None

    @classmethod
    def get_by_id(cls, session: Session, id: int) -> Optional[T]:
        """
        Obtém um registro por ID.
        
        Args:
            session: Sessão do banco de dados
            id: ID do registro
        
        Returns:
            Objeto encontrado ou None
        """
        return session.get(cls.model, id)

    @classmethod
    def get_all(cls, session: Session, skip: int = 0, limit: int = 100) -> List[T]:
        """
        Obtém todos os registros com paginação.
        
        Args:
            session: Sessão do banco de dados
            skip: Número de registros a pular
            limit: Limite de registros a retornar
        
        Returns:
            Lista de registros
        """
        statement = select(cls.model).offset(skip).limit(limit)
        return session.exec(statement).all()

    @classmethod
    def create(cls, session: Session, obj: T) -> T:
        """
        Cria um novo registro.
        
        Args:
            session: Sessão do banco de dados
            obj: Objeto a criar
        
        Returns:
            Objeto criado
        """
        session.add(obj)
        session.commit()
        session.refresh(obj)
        logger.debug(f"Criado novo {cls.model.__name__}: {obj.id}")
        return obj

    @classmethod
    def update(cls, session: Session, id: int, data: dict) -> Optional[T]:
        """
        Atualiza um registro.
        
        Args:
            session: Sessão do banco de dados
            id: ID do registro
            data: Dicionário com dados a atualizar
        
        Returns:
            Objeto atualizado ou None se não encontrado
        """
        obj = session.get(cls.model, id)
        if not obj:
            return None
        
        for key, value in data.items():
            if value is not None and hasattr(obj, key):
                setattr(obj, key, value)
        
        obj.updated_at = datetime.now(timezone.utc)
        session.commit()
        session.refresh(obj)
        logger.debug(f"Atualizado {cls.model.__name__}: {obj.id}")
        return obj

    @classmethod
    def delete(cls, session: Session, id: int) -> bool:
        """
        Deleta um registro.
        
        Args:
            session: Sessão do banco de dados
            id: ID do registro
        
        Returns:
            True se deletado, False se não encontrado
        """
        obj = session.get(cls.model, id)
        if not obj:
            return False
        
        session.delete(obj)
        session.commit()
        logger.debug(f"Deletado {cls.model.__name__}: {id}")
        return True


class RoomRepository(BaseRepository[Room]):
    """Repositório para gerenciamento de salas."""
    model = Room

    @staticmethod
    def get_active_rooms(session: Session) -> List[Room]:
        """
        Retorna todas as salas ativas.
        
        Args:
            session: Sessão do banco de dados
        
        Returns:
            Lista de salas ativas
        """
        stmt = select(Room).where(Room.active == True).order_by(Room.name)
        return session.exec(stmt).all()

    @staticmethod
    def get_by_name(session: Session, name: str) -> Optional[Room]:
        """
        Obtém sala pelo nome.
        
        Args:
            session: Sessão do banco de dados
            name: Nome da sala
        
        Returns:
            Sala encontrada ou None
        """
        stmt = select(Room).where(Room.name == name)
        return session.exec(stmt).first()


class PatientRepository(BaseRepository[Patient]):
    """Repositório para gerenciamento de pacientes."""
    model = Patient

    @staticmethod
    def get_active_patients(session: Session) -> List[Patient]:
        """
        Retorna todos os pacientes ativos.
        
        Args:
            session: Sessão do banco de dados
        
        Returns:
            Lista de pacientes ativos
        """
        stmt = select(Patient).where(Patient.active == True).order_by(Patient.name)
        return session.exec(stmt).all()

    @staticmethod
    def get_by_email(session: Session, email: str) -> Optional[Patient]:
        """
        Obtém paciente pelo email.
        
        Args:
            session: Sessão do banco de dados
            email: Email do paciente
        
        Returns:
            Paciente encontrado ou None
        """
        stmt = select(Patient).where(Patient.email == email)
        return session.exec(stmt).first()

    @staticmethod
    def get_children(session: Session) -> List[Patient]:
        """
        Retorna todos os pacientes infantojuvenis.
        
        Args:
            session: Sessão do banco de dados
        
        Returns:
            Lista de pacientes infantojuvenis
        """
        stmt = (
            select(Patient)
            .where((Patient.is_child == True) & (Patient.active == True))
            .order_by(Patient.name)
        )
        return session.exec(stmt).all()


class UserRepository(BaseRepository[User]):
    """Repositório para gerenciamento de usuários."""
    model = User

    @staticmethod
    def get_by_email(session: Session, email: str) -> Optional[User]:
        """
        Obtém usuário pelo email.
        
        Args:
            session: Sessão do banco de dados
            email: Email do usuário
        
        Returns:
            Usuário encontrado ou None
        """
        stmt = select(User).where(User.email == email.lower())
        return session.exec(stmt).first()

    @staticmethod
    def get_active_users(session: Session) -> List[User]:
        """
        Retorna todos os usuários ativos.
        
        Args:
            session: Sessão do banco de dados
        
        Returns:
            Lista de usuários ativos
        """
        stmt = select(User).where(User.is_active == True).order_by(User.name)
        return session.exec(stmt).all()


class AppointmentRepository(BaseRepository[Appointment]):
    """Repositório para gerenciamento de agendamentos."""
    model = Appointment

    @staticmethod
    def get_active_appointments(session: Session, skip: int = 0, limit: int = 100) -> List[Appointment]:
        """
        Retorna agendamentos ativos (não deletados e não cancelados).
        
        Args:
            session: Sessão do banco de dados
            skip: Número de registros a pular
            limit: Limite de registros
        
        Returns:
            Lista de agendamentos ativos
        """
        stmt = (
            select(Appointment)
            .where(
                (Appointment.is_deleted == False)
                & (Appointment.status != AppointmentStatus.CANCELLED)
            )
            .order_by(Appointment.start_dt)
            .offset(skip)
            .limit(limit)
        )
        return session.exec(stmt).all()

    @staticmethod
    def get_by_room_and_time(
        session: Session, room_id: int, start: datetime, end: datetime
    ) -> List[Appointment]:
        """
        Retorna agendamentos de uma sala em período específico.
        
        Args:
            session: Sessão do banco de dados
            room_id: ID da sala
            start: Data/hora inicial
            end: Data/hora final
        
        Returns:
            Lista de agendamentos conflitantes
        """
        stmt = (
            select(Appointment)
            .where(
                (Appointment.room_id == room_id)
                & (Appointment.start_dt < end)
                & (Appointment.end_dt > start)
                & (Appointment.is_deleted == False)
                & (Appointment.status != AppointmentStatus.CANCELLED)
            )
            .order_by(Appointment.start_dt)
        )
        return session.exec(stmt).all()

    @staticmethod
    def get_by_student_and_time(
        session: Session, student_id: int, start: datetime, end: datetime
    ) -> List[Appointment]:
        """
        Retorna agendamentos de um estagiário em período específico.
        
        Args:
            session: Sessão do banco de dados
            student_id: ID do estagiário
            start: Data/hora inicial
            end: Data/hora final
        
        Returns:
            Lista de agendamentos do estagiário
        """
        stmt = (
            select(Appointment)
            .where(
                (Appointment.student_id == student_id)
                & (Appointment.start_dt < end)
                & (Appointment.end_dt > start)
                & (Appointment.is_deleted == False)
                & (Appointment.status != AppointmentStatus.CANCELLED)
            )
            .order_by(Appointment.start_dt)
        )
        return session.exec(stmt).all()

    @staticmethod
    def get_by_supervisor_and_time(
        session: Session, supervisor_id: int, start: datetime, end: datetime
    ) -> List[Appointment]:
        """
        Retorna agendamentos de um supervisor em período específico.
        
        Args:
            session: Sessão do banco de dados
            supervisor_id: ID do supervisor
            start: Data/hora inicial
            end: Data/hora final
        
        Returns:
            Lista de agendamentos do supervisor
        """
        stmt = (
            select(Appointment)
            .where(
                (Appointment.supervisor_id == supervisor_id)
                & (Appointment.start_dt < end)
                & (Appointment.end_dt > start)
                & (Appointment.is_deleted == False)
                & (Appointment.status != AppointmentStatus.CANCELLED)
            )
            .order_by(Appointment.start_dt)
        )
        return session.exec(stmt).all()

    @staticmethod
    def soft_delete(session: Session, id: int) -> bool:
        """
        Soft delete - marca como deletado sem remover do banco.
        
        Args:
            session: Sessão do banco de dados
            id: ID do agendamento
        
        Returns:
            True se deletado, False se não encontrado
        """
        appointment = session.get(Appointment, id)
        if not appointment:
            return False
        
        appointment.is_deleted = True
        appointment.updated_at = datetime.now(timezone.utc)
        session.commit()
        logger.debug(f"Agendamento deletado (soft): {id}")
        return True

    @staticmethod
    def get_by_patient(session: Session, patient_id: int) -> List[Appointment]:
        """
        Retorna todos os agendamentos de um paciente.
        
        Args:
            session: Sessão do banco de dados
            patient_id: ID do paciente
        
        Returns:
            Lista de agendamentos do paciente
        """
        stmt = (
            select(Appointment)
            .where(
                (Appointment.patient_id == patient_id) & (Appointment.is_deleted == False)
            )
            .order_by(Appointment.start_dt.desc())
        )
        return session.exec(stmt).all()

    @staticmethod
    def get_future_appointments(session: Session) -> List[Appointment]:
        """
        Retorna agendamentos futuros.
        
        Args:
            session: Sessão do banco de dados
        
        Returns:
            Lista de agendamentos futuros
        """
        now = datetime.now(timezone.utc)
        stmt = (
            select(Appointment)
            .where(
                (Appointment.start_dt >= now)
                & (Appointment.is_deleted == False)
                & (Appointment.status != AppointmentStatus.CANCELLED)
            )
            .order_by(Appointment.start_dt)
        )
        return session.exec(stmt).all()

