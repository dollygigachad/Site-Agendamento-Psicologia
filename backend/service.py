"""Camada de serviço - regras de negócio da aplicação."""
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Tuple
from sqlmodel import Session, select
from backend.models import Room, Patient, User, Appointment
from backend.repository import (
    RoomRepository,
    AppointmentRepository,
)
from backend.enums import AppointmentStatus, UserRole
from backend.enums import minutes_between, get_day_start, get_day_end
from .config import get_settings
from .logger import logger

settings = get_settings()


class AppointmentService:
    """Serviço de agendamento com validações de negócio."""

    @staticmethod
    def validate_appointment_creation(
        session: Session,
        start_dt: datetime,
        end_dt: datetime,
        room_id: int,
        student_id: int,
        supervisor_id: int,
        patient_id: int,
    ) -> Tuple[bool, Optional[str]]:
        """
        Valida criação de agendamento com todas as regras de negócio.
        
        Args:
            session: Sessão do banco de dados
            start_dt: Data/hora de início
            end_dt: Data/hora de fim
            room_id: ID da sala
            student_id: ID do estagiário
            supervisor_id: ID do supervisor
            patient_id: ID do paciente
        
        Returns:
            Tupla (válido, mensagem_erro)
        """
        # 1. Validar datas
        if start_dt >= end_dt:
            logger.warning("Tentativa de criar agendamento com data inválida")
            return False, "Data de fim deve ser posterior à data de início."

        duration_minutes = minutes_between(start_dt, end_dt)
        
        if duration_minutes > settings.MAX_APPOINTMENT_DURATION_MINUTES:
            return False, (
                f"Duração máxima de agendamento é "
                f"{settings.MAX_APPOINTMENT_DURATION_MINUTES} minutos."
            )

        if duration_minutes < settings.MIN_APPOINTMENT_DURATION_MINUTES:
            return False, (
                f"Duração mínima de agendamento é "
                f"{settings.MIN_APPOINTMENT_DURATION_MINUTES} minutos."
            )

        # 2. Validar entidades existem e estão ativas
        room = session.get(Room, room_id)
        if not room or not room.active:
            logger.warning(f"Sala {room_id} não encontrada ou inativa")
            return False, "Sala não encontrada ou inativa."

        patient = session.get(Patient, patient_id)
        if not patient or not patient.active:
            logger.warning(f"Paciente {patient_id} não encontrado ou inativo")
            return False, "Paciente não encontrado ou inativo."

        student = session.get(User, student_id)
        if (
            not student
            or not student.is_active
            or student.role != UserRole.STUDENT
        ):
            logger.warning(f"Estagiário {student_id} não encontrado ou inativo")
            return False, "Estagiário não encontrado ou inativo."

        supervisor = session.get(User, supervisor_id)
        if (
            not supervisor
            or not supervisor.is_active
            or supervisor.role != UserRole.PROFESSOR
        ):
            logger.warning(f"Supervisor {supervisor_id} não encontrado ou inativo")
            return False, "Supervisor não encontrado ou inativo."

        # 3. Validar conflitos de horário
        conflicts = AppointmentService.check_conflicts(
            session, start_dt, end_dt, room_id, student_id, supervisor_id
        )
        if conflicts:
            logger.warning(f"Conflitos detectados: {conflicts}")
            return False, f"Conflito de horário detectado: {', '.join(conflicts)}"

        # 4. Validar limite de horas do estagiário por dia
        max_reached, hours = AppointmentService.check_student_daily_limit(
            session, student_id, start_dt
        )
        if max_reached:
            logger.warning(
                f"Estagiário {student_id} atingiu limite diário: {hours}h"
            )
            return False, (
                f"Estagiário atingiu limite de "
                f"{settings.MAX_STUDENT_HOURS_PER_DAY}h por dia. "
                f"Horas agendadas: {hours:.1f}h"
            )

        logger.info(f"Validação de agendamento aprovada para sala {room_id}")
        return True, None

    @staticmethod
    def check_conflicts(
        session: Session,
        start_dt: datetime,
        end_dt: datetime,
        room_id: int,
        student_id: int,
        supervisor_id: int,
    ) -> List[str]:
        """
        Verifica todos os conflitos possíveis de agendamento.
        
        Args:
            session: Sessão do banco de dados
            start_dt: Data/hora de início
            end_dt: Data/hora de fim
            room_id: ID da sala
            student_id: ID do estagiário
            supervisor_id: ID do supervisor
        
        Returns:
            Lista com descrição dos conflitos encontrados
        """
        conflicts = []

        # Conflito de sala
        room_conflicts = AppointmentRepository.get_by_room_and_time(
            session, room_id, start_dt, end_dt
        )
        if room_conflicts:
            conflicts.append(f"Sala ocupada ({len(room_conflicts)} agendamentos)")

        # Conflito de estagiário
        student_conflicts = AppointmentRepository.get_by_student_and_time(
            session, student_id, start_dt, end_dt
        )
        if student_conflicts:
            conflicts.append(
                f"Estagiário indisponível ({len(student_conflicts)} agendamentos)"
            )

        # Conflito de supervisor
        supervisor_conflicts = AppointmentRepository.get_by_supervisor_and_time(
            session, supervisor_id, start_dt, end_dt
        )
        if supervisor_conflicts:
            conflicts.append(
                f"Supervisor indisponível ({len(supervisor_conflicts)} agendamentos)"
            )

        return conflicts

    @staticmethod
    def check_student_daily_limit(
        session: Session, student_id: int, start_dt: datetime
    ) -> Tuple[bool, float]:
        """
        Verifica se estagiário atingiu limite de horas por dia.
        
        Args:
            session: Sessão do banco de dados
            student_id: ID do estagiário
            start_dt: Data de referência
        
        Returns:
            Tupla (limite_atingido, horas_totais)
        """
        day_start = get_day_start(start_dt)
        day_end = get_day_end(start_dt)

        appointments = AppointmentRepository.get_by_student_and_time(
            session, student_id, day_start, day_end
        )

        total_minutes = sum(
            minutes_between(ap.start_dt, ap.end_dt) for ap in appointments
        )
        total_hours = total_minutes / 60

        max_reached = total_hours >= settings.MAX_STUDENT_HOURS_PER_DAY
        return max_reached, total_hours


class RoomService:
    """Serviço de gerenciamento de salas."""

    @staticmethod
    def get_available_rooms(
        session: Session, start_dt: datetime, end_dt: datetime
    ) -> List[Room]:
        """
        Retorna salas disponíveis em um período específico.
        
        Args:
            session: Sessão do banco de dados
            start_dt: Data/hora de início
            end_dt: Data/hora de fim
        
        Returns:
            Lista de salas disponíveis
        """
        all_rooms = RoomRepository.get_active_rooms(session)
        available = []

        for room in all_rooms:
            conflicts = AppointmentRepository.get_by_room_and_time(
                session, room.id, start_dt, end_dt
            )
            if not conflicts:
                available.append(room)

        return available

    @staticmethod
    def get_room_occupancy(
        session: Session, room_id: int, start_dt: datetime, end_dt: datetime
    ) -> dict:
        """
        Retorna informações de ocupação de uma sala.
        
        Args:
            session: Sessão do banco de dados
            room_id: ID da sala
            start_dt: Data/hora de início
            end_dt: Data/hora de fim
        
        Returns:
            Dicionário com informações de ocupação
        """
        appointments = AppointmentRepository.get_by_room_and_time(
            session, room_id, start_dt, end_dt
        )
        total_minutes = sum(
            minutes_between(ap.start_dt, ap.end_dt) for ap in appointments
        )

        return {
            "room_id": room_id,
            "appointments_count": len(appointments),
            "total_minutes_occupied": int(total_minutes),
            "total_hours_occupied": total_minutes / 60,
        }


class StudentService:
    """Serviço de gerenciamento de estagiários."""

    @staticmethod
    def get_availability(
        session: Session, student_id: int, date: datetime
    ) -> dict:
        """
        Retorna resumo de disponibilidade do estagiário em um dia.
        
        Args:
            session: Sessão do banco de dados
            student_id: ID do estagiário
            date: Data de referência
        
        Returns:
            Dicionário com informações de disponibilidade
        """
        day_start = get_day_start(date)
        day_end = get_day_end(date)

        appointments = AppointmentRepository.get_by_student_and_time(
            session, student_id, day_start, day_end
        )

        total_minutes = sum(
            minutes_between(ap.start_dt, ap.end_dt) for ap in appointments
        )
        total_hours = total_minutes / 60

        return {
            "date": date.date(),
            "appointments_count": len(appointments),
            "total_hours": round(total_hours, 2),
            "available_hours": round(
                max(0, settings.MAX_STUDENT_HOURS_PER_DAY - total_hours), 2
            ),
            "is_full": total_hours >= settings.MAX_STUDENT_HOURS_PER_DAY,
        }

    @staticmethod
    def get_load_balance(
        session: Session, student_id: int, days: int = 30
    ) -> dict:
        """
        Retorna balanceamento de carga do estagiário.
        
        Args:
            session: Sessão do banco de dados
            student_id: ID do estagiário
            days: Número de dias a considerar
        
        Returns:
            Dicionário com informações de balanceamento
        """
        start = datetime.now(timezone.utc)
        end = start + timedelta(days=days)

        stmt = select(Appointment).where(
            (Appointment.student_id == student_id)
            & (Appointment.start_dt >= start)
            & (Appointment.end_dt <= end)
            & (Appointment.is_deleted == False)
            & (Appointment.status != AppointmentStatus.CANCELLED)
        )

        appointments = session.exec(stmt).all()

        total_minutes = sum(
            minutes_between(ap.start_dt, ap.end_dt) for ap in appointments
        )
        total_hours = total_minutes / 60
        avg_per_day = total_hours / days if days > 0 else 0

        return {
            "period_days": days,
            "total_appointments": len(appointments),
            "total_hours": round(total_hours, 2),
            "average_hours_per_day": round(avg_per_day, 2),
        }

