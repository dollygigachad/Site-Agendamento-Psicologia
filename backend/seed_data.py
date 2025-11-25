"""Script para popular banco de dados com dados de teste."""
from datetime import datetime, timedelta, timezone
from .models import Room, Patient, User, Appointment
from .security import hash_password
from .enums import UserRole, AppointmentStatus
from .logger import logger


def seed_database():
    """Popula banco de dados com dados iniciais."""
    from .database import get_session_context
    from sqlmodel import select

    try:
        with get_session_context() as session:
            # Verificar se já existe dados
            count = session.exec(select(Room)).first()
            if count:
                # Se já existem dados, garantir que registros essenciais estejam ativos
                from sqlmodel import select
                inactive_patients = session.exec(select(Patient).where(Patient.active == False)).all()
                if inactive_patients:
                    for p in inactive_patients:
                        p.active = True
                    session.commit()
                    logger.info(f"Atualizados {len(inactive_patients)} pacientes para active=True")

                inactive_users = session.exec(select(User).where(User.is_active == False)).all()
                if inactive_users:
                    for u in inactive_users:
                        u.is_active = True
                    session.commit()
                    logger.info(f"Atualizados {len(inactive_users)} usuários para is_active=True")

                logger.info("Banco de dados já contém dados. Pulando criação inicial de seed.")
                return

            # Criar Salas
            rooms = [
                Room(name="Sala Azul", description="Sala de atendimento individual", capacity=1),
                Room(name="Sala Verde", description="Sala de atendimento em grupo", capacity=4),
                Room(name="Sala Amarela", description="Sala de observação", capacity=2),
            ]
            session.add_all(rooms)
            session.commit()
            logger.info(f"✓ {len(rooms)} salas criadas")

            # Criar Pacientes
            patients = [
                Patient(name="João Silva", email="joao@email.com", is_child=False, active=True),
                Patient(name="Maria Santos", email="maria@email.com", is_child=False, active=True),
                Patient(name="Lucas Oliveira", email="lucas@email.com", is_child=True, active=True),
                Patient(name="Ana Costa", email="ana@email.com", is_child=True, active=True),
            ]
            session.add_all(patients)
            session.commit()
            logger.info(f"✓ {len(patients)} pacientes criados")

            # Criar Usuários (estagiários e professores)
            users = [
                User(
                    name="Carlos Pereira",
                    email="carlos@unipar.br",
                    hashed_password=hash_password("senha123"),
                    role=UserRole.STUDENT,
                    is_active=True
                ),
                User(
                    name="Amanda Rodriguez",
                    email="amanda@unipar.br",
                    hashed_password=hash_password("senha123"),
                    role=UserRole.STUDENT,
                    is_active=True
                ),
                User(
                    name="Prof. Patricia Lima",
                    email="patricia@unipar.br",
                    hashed_password=hash_password("senha123"),
                    role=UserRole.PROFESSOR,
                    is_active=True
                ),
                User(
                    name="Prof. Roberto Santos",
                    email="roberto@unipar.br",
                    hashed_password=hash_password("senha123"),
                    role=UserRole.PROFESSOR,
                    is_active=True
                ),
                User(
                    name="Admin Sistema",
                    email="admin@unipar.br",
                    hashed_password=hash_password("admin123"),
                    role=UserRole.ADMIN,
                    is_active=True
                ),
            ]
            session.add_all(users)
            session.commit()
            logger.info(f"✓ {len(users)} usuários criados")

            # Refresh para obter IDs
            for room in rooms:
                session.refresh(room)
            for patient in patients:
                session.refresh(patient)
            for user in users:
                session.refresh(user)

            # Criar alguns Agendamentos
            now = datetime.now(timezone.utc)
            appointments = [
                Appointment(
                    start_dt=now + timedelta(hours=1),
                    end_dt=now + timedelta(hours=2),
                    status=AppointmentStatus.SCHEDULED,
                    room_id=rooms[0].id,
                    patient_id=patients[0].id,
                    student_id=users[0].id,
                    supervisor_id=users[2].id,
                    notes="Primeiro atendimento"
                ),
                Appointment(
                    start_dt=now + timedelta(hours=3),
                    end_dt=now + timedelta(hours=4),
                    status=AppointmentStatus.SCHEDULED,
                    room_id=rooms[1].id,
                    patient_id=patients[1].id,
                    student_id=users[1].id,
                    supervisor_id=users[3].id,
                    notes="Atendimento em grupo"
                ),
            ]
            session.add_all(appointments)
            session.commit()
            logger.info(f"✓ {len(appointments)} agendamentos criados")

            logger.info("✓ Banco de dados populado com sucesso!")
            return
    except Exception as e:
        logger.error(f"Erro ao popular banco de dados: {e}")
        raise


if __name__ == "__main__":
    from .database import create_db_and_tables
    create_db_and_tables()
    seed_database()


