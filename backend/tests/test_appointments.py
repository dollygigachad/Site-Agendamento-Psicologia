"""Testes de validação de agendamento."""
from datetime import datetime, timedelta, timezone
from sqlmodel import create_engine, SQLModel, Session
from backend.models import Room, Patient, User, Appointment
from backend.service import AppointmentService
from backend.enums import UserRole
from backend.config import get_settings

# Engine em memória para testes
TEST_ENGINE = create_engine("sqlite:///:memory:")
settings = get_settings()

def setup_test_db():
    """Configura banco de teste com dados iniciais."""
    # Garantir DB limpo por teste
    SQLModel.metadata.drop_all(TEST_ENGINE)
    SQLModel.metadata.create_all(TEST_ENGINE)
    session = Session(TEST_ENGINE)
    
    # Criar dados de teste
    room = Room(name="Sala 1", capacity=1)
    patient = Patient(name="Paciente Teste")
    student = User(name="Estagiário Teste", email="student@test.com", hashed_password="hash", role=UserRole.STUDENT)
    supervisor = User(name="Professor Teste", email="prof@test.com", hashed_password="hash", role=UserRole.PROFESSOR)
    
    session.add_all([room, patient, student, supervisor])
    session.commit()
    session.refresh(room)
    session.refresh(patient)
    session.refresh(student)
    session.refresh(supervisor)
    
    return session, room, patient, student, supervisor

def test_valid_appointment():
    """Testa criação de agendamento válido."""
    session, room, patient, student, supervisor = setup_test_db()
    
    now = datetime.now(timezone.utc)
    start = now + timedelta(hours=1)
    end = start + timedelta(hours=1)
    
    valid, error = AppointmentService.validate_appointment_creation(
        session, start, end, room.id, student.id, supervisor.id, patient.id
    )
    
    assert valid is True, f"Agendamento válido foi rejeitado: {error}"
    session.close()

def test_end_before_start():
    """Testa agendamento com fim antes do início."""
    session, room, patient, student, supervisor = setup_test_db()
    
    now = datetime.now(timezone.utc)
    start = now + timedelta(hours=2)
    end = now + timedelta(hours=1)
    
    valid, error = AppointmentService.validate_appointment_creation(
        session, start, end, room.id, student.id, supervisor.id, patient.id
    )
    
    assert valid is False
    assert "posterior" in error.lower()
    session.close()

def test_duration_too_short():
    """Testa agendamento menor que 30 minutos."""
    session, room, patient, student, supervisor = setup_test_db()
    
    now = datetime.now(timezone.utc)
    start = now + timedelta(hours=1)
    end = start + timedelta(minutes=15)
    
    valid, error = AppointmentService.validate_appointment_creation(
        session, start, end, room.id, student.id, supervisor.id, patient.id
    )
    
    assert valid is False
    assert "30" in error
    session.close()

def test_room_conflict():
    """Testa conflito de sala."""
    session, room, patient, student, supervisor = setup_test_db()
    
    # Criar agendamento inicial
    now = datetime.now(timezone.utc)
    start1 = now + timedelta(hours=1)
    end1 = start1 + timedelta(hours=1)
    
    ap1 = Appointment(
        start_dt=start1, end_dt=end1,
        room_id=room.id, patient_id=patient.id,
        student_id=student.id, supervisor_id=supervisor.id
    )
    session.add(ap1)
    session.commit()
    session.refresh(ap1)
    
    # Tentar agendar ao mesmo tempo na mesma sala
    start2 = start1 + timedelta(minutes=30)
    end2 = start2 + timedelta(hours=1)
    
    valid, error = AppointmentService.validate_appointment_creation(
        session, start2, end2, room.id, student.id, supervisor.id, patient.id
    )
    
    assert valid is False
    assert "conflito" in error.lower()
    session.close()

def test_student_daily_limit():
    """Testa limite de horas do estagiário por dia."""
    session, room, patient, student, supervisor = setup_test_db()
    
    now = datetime.now(timezone.utc)
    
    # Criar 4 agendamentos de 1 hora cada (máximo = 4)
    for i in range(4):
        start = now.replace(hour=9) + timedelta(hours=i)
        end = start + timedelta(hours=1)
        ap = Appointment(
            start_dt=start, end_dt=end,
            room_id=room.id, patient_id=patient.id,
            student_id=student.id, supervisor_id=supervisor.id
        )
        session.add(ap)
    session.commit()
    
    # Tentar agendar mais um no mesmo dia
    start_extra = now.replace(hour=13)
    end_extra = start_extra + timedelta(hours=1)
    
    valid, error = AppointmentService.validate_appointment_creation(
        session, start_extra, end_extra, room.id, student.id, supervisor.id, patient.id
    )
    
    assert valid is False
    assert "limite" in error.lower()
    session.close()

def test_student_availability():
    """Testa cálculo de disponibilidade de estagiário."""
    from backend.service import StudentService
    session, room, patient, student, supervisor = setup_test_db()
    
    now = datetime.now(timezone.utc)
    test_date = now.replace(hour=0, minute=0, second=0)
    
    # Agendar 2 horas
    start = test_date.replace(hour=9)
    end = start + timedelta(hours=2)
    ap = Appointment(
        start_dt=start, end_dt=end,
        room_id=room.id, patient_id=patient.id,
        student_id=student.id, supervisor_id=supervisor.id
    )
    session.add(ap)
    session.commit()
    
    # Verificar disponibilidade
    avail = StudentService.get_availability(session, student.id, test_date)
    
    assert avail["total_hours"] == 2.0
    assert avail["available_hours"] == 2.0  # 4 - 2
    session.close()


