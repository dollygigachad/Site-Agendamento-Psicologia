from datetime import datetime, timedelta
from sqlmodel import create_engine, SQLModel, Session
from backend.models import Room, Patient, User, Appointment
from backend.enums import UserRole
from backend.utils import has_conflict

# Use in-memory sqlite for tests
ENGINE = create_engine("sqlite:///:memory:")

def setup_db():
    SQLModel.metadata.create_all(ENGINE)
    session = Session(ENGINE)
    r = Room(name='Sala 1')
    p = Patient(name='Paciente 1')
    s = User(name='Estagiario 1', email='est1@test.com', hashed_password='hash', role=UserRole.STUDENT)
    sup = User(name='Supervisor 1', email='sup1@test.com', hashed_password='hash', role=UserRole.PROFESSOR)
    session.add_all([r,p,s,sup])
    session.commit()
    session.refresh(r)
    session.refresh(p)
    session.refresh(s)
    session.refresh(sup)
    return session, r, p, s, sup

def test_conflict_detected():
    session, r, p, s, sup = setup_db()
    now = datetime.now()
    ap1 = Appointment(start_dt=now, end_dt=now + timedelta(hours=1), room_id=r.id, patient_id=p.id, student_id=s.id, supervisor_id=sup.id)
    session.add(ap1); session.commit(); session.refresh(ap1)

    # overlapping appointment (same room)
    start2 = now + timedelta(minutes=30)
    end2 = start2 + timedelta(hours=1)
    assert has_conflict(session, start2, end2, r.id, None, None) is True

    # non-overlapping (after)
    start3 = now + timedelta(hours=2)
    end3 = start3 + timedelta(hours=1)
    assert has_conflict(session, start3, end3, r.id, None, None) is False

    session.close()


