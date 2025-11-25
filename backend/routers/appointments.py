"""Router para gerenciamento de agendamentos."""
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, status, Depends, Query
from sqlmodel import Session
from ..models import Appointment, User
from ..schemas import AppointmentCreate, AppointmentUpdate, AppointmentResponse, AppointmentListResponse
from ..repository import AppointmentRepository
from ..service import AppointmentService, RoomService, StudentService
from ..database import get_session
from ..logger import logger

router = APIRouter(prefix="/api/appointments", tags=["appointments"])

@router.get("", response_model=List[AppointmentListResponse])
def list_appointments(
    skip: int = 0,
    limit: int = 100,
    student_id: Optional[int] = Query(None),
    room_id: Optional[int] = Query(None),
    session: Session = Depends(get_session)
):
    """Lista agendamentos com filtros opcionais."""
    from sqlmodel import select
    
    stmt = (
        select(Appointment)
        .where(
            (Appointment.is_deleted == False)
        )
    )
    
    if student_id:
        stmt = stmt.where(Appointment.student_id == student_id)
    if room_id:
        stmt = stmt.where(Appointment.room_id == room_id)
    
    stmt = stmt.offset(skip).limit(limit).order_by(Appointment.start_dt)
    appointments = session.exec(stmt).all()
    
    results = []
    for ap in appointments:
        student_name = None
        supervisor_name = None
        try:
            if getattr(ap, 'student_id', None):
                student = session.get(User, ap.student_id)
                student_name = student.name if student else None
            if getattr(ap, 'supervisor_id', None):
                supervisor = session.get(User, ap.supervisor_id)
                supervisor_name = supervisor.name if supervisor else None
        except Exception as e:
            logger.error(f"Erro ao recuperar usuarios do agendamento {ap.id}: {str(e)}")
            student_name = None
            supervisor_name = None

        results.append(
            AppointmentListResponse(
                id=ap.id,
                start_dt=ap.start_dt,
                end_dt=ap.end_dt,
                status=ap.status,
                room_name=ap.room.name if ap.room else None,
                patient_name=ap.patient.name if ap.patient else None,
                student_name=student_name,
                supervisor_name=supervisor_name,
            )
        )

    return results

@router.get("/{appointment_id}", response_model=AppointmentResponse)
def get_appointment(appointment_id: int, session: Session = Depends(get_session)):
    """Obtem agendamento por ID."""
    appointment = session.get(Appointment, appointment_id)
    if not appointment or appointment.is_deleted:
        raise HTTPException(status_code=404, detail="Agendamento nao encontrado")
    return appointment

@router.post("", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED)
def create_appointment(
    appointment_data: AppointmentCreate,
    session: Session = Depends(get_session)
):
    """Cria novo agendamento com validacoes completas."""
    from ..models import Room, Patient
    
    if not session.get(Room, appointment_data.room_id):
        raise HTTPException(status_code=404, detail="Sala nao encontrada")
    if not session.get(Patient, appointment_data.patient_id):
        raise HTTPException(status_code=404, detail="Paciente nao encontrado")
    if not session.get(User, appointment_data.student_id):
        raise HTTPException(status_code=404, detail="Estagiario nao encontrado")
    if not session.get(User, appointment_data.supervisor_id):
        raise HTTPException(status_code=404, detail="Supervisor nao encontrado")
    
    valid, error_msg = AppointmentService.validate_appointment_creation(
        session,
        appointment_data.start_dt,
        appointment_data.end_dt,
        appointment_data.room_id,
        appointment_data.student_id,
        appointment_data.supervisor_id,
        appointment_data.patient_id
    )
    
    if not valid:
        logger.warning(f"Criacao de agendamento rejeitada: {error_msg}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )
    
    appointment = Appointment(**appointment_data.dict())
    appointment = AppointmentRepository.create(session, appointment)
    logger.info(f"Agendamento criado: ID {appointment.id}")

    # Preencher os campos student e supervisor para o response model
    student = session.get(User, appointment.student_id) if appointment.student_id else None
    supervisor = session.get(User, appointment.supervisor_id) if appointment.supervisor_id else None
    room = session.get(Room, appointment.room_id) if appointment.room_id else None
    patient = session.get(Patient, appointment.patient_id) if appointment.patient_id else None

    return AppointmentResponse(
        id=appointment.id,
        start_dt=appointment.start_dt,
        end_dt=appointment.end_dt,
        status=appointment.status,
        notes=appointment.notes,
        room=room,
        patient=patient,
        student=student,
        supervisor=supervisor,
        created_at=appointment.created_at,
        updated_at=appointment.updated_at,
    )

@router.put("/{appointment_id}", response_model=AppointmentResponse)
def update_appointment(
    appointment_id: int,
    appointment_data: AppointmentUpdate,
    session: Session = Depends(get_session)
):
    """Atualiza agendamento (apenas status e notas)."""
    appointment = session.get(Appointment, appointment_id)
    if not appointment or appointment.is_deleted:
        raise HTTPException(status_code=404, detail="Agendamento nao encontrado")
    
    appointment = AppointmentRepository.update(
        session,
        appointment_id,
        appointment_data.dict(exclude_unset=True)
    )
    logger.info(f"Agendamento atualizado: ID {appointment.id}")
    return appointment

@router.delete("/{appointment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_appointment(appointment_id: int, session: Session = Depends(get_session)):
    """Deleta agendamento (soft delete)."""
    appointment = session.get(Appointment, appointment_id)
    if not appointment:
        raise HTTPException(status_code=404, detail="Agendamento nao encontrado")
    
    AppointmentRepository.soft_delete(session, appointment_id)
    logger.info(f"Agendamento deletado: ID {appointment_id}")
    return None

@router.get("/student/{student_id}/availability", response_model=dict)
def get_student_availability(
    student_id: int,
    date: str = Query(...),
    session: Session = Depends(get_session)
):
    """Obtem disponibilidade de um estagiario em um dia."""
    from datetime import datetime
    date_obj = datetime.fromisoformat(date)
    availability = StudentService.get_availability(session, student_id, date_obj)
    return availability

@router.get("/student/{student_id}/load-balance", response_model=dict)
def get_student_load_balance(
    student_id: int,
    days: int = Query(30, ge=1, le=365),
    session: Session = Depends(get_session)
):
    """Obtem balanceamento de carga de um estagiario."""
    balance = StudentService.get_load_balance(session, student_id, days)
    return balance

@router.get("/rooms/available", response_model=List[AppointmentListResponse])
def get_available_rooms(
    start_dt: str = Query(...),
    end_dt: str = Query(...),
    session: Session = Depends(get_session)
):
    """Lista salas disponiveis em periodo."""
    from datetime import datetime
    start_obj = datetime.fromisoformat(start_dt)
    end_obj = datetime.fromisoformat(end_dt)
    available = RoomService.get_available_rooms(session, start_obj, end_obj)
    return [{"id": r.id, "name": r.name} for r in available]




