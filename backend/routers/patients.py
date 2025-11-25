"""Router para gerenciamento de pacientes."""
from typing import List
from fastapi import APIRouter, HTTPException, status, Depends
from sqlmodel import Session
from ..models import Patient
from ..schemas import PatientCreate, PatientUpdate, PatientResponse
from ..repository import PatientRepository
from ..database import get_session
from ..logger import logger

router = APIRouter(prefix="/api/patients", tags=["patients"])

@router.get("", response_model=List[PatientResponse])
def list_patients(skip: int = 0, limit: int = 100, session: Session = Depends(get_session)):
    """Lista todos os pacientes."""
    patients = PatientRepository.get_active_patients(session)
    return patients[skip : skip + limit]

@router.get("/{patient_id}", response_model=PatientResponse)
def get_patient(patient_id: int, session: Session = Depends(get_session)):
    """Obtém paciente por ID."""
    patient = session.get(Patient, patient_id)
    if not patient or not patient.active:
        raise HTTPException(status_code=404, detail="Paciente não encontrado")
    return patient

@router.post("", response_model=PatientResponse, status_code=status.HTTP_201_CREATED)
def create_patient(patient_data: PatientCreate, session: Session = Depends(get_session)):
    """Cria novo paciente."""
    patient = Patient(**patient_data.model_dump())
    patient = PatientRepository.create(session, patient)
    logger.info(f"Novo paciente criado: {patient.name}")
    return patient

@router.put("/{patient_id}", response_model=PatientResponse)
def update_patient(patient_id: int, patient_data: PatientUpdate, session: Session = Depends(get_session)):
    """Atualiza paciente."""
    patient = session.get(Patient, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Paciente não encontrado")
    
    patient = PatientRepository.update(session, patient_id, patient_data.dict(exclude_unset=True))
    logger.info(f"Paciente atualizado: {patient.name}")
    return patient

@router.delete("/{patient_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_patient(patient_id: int, session: Session = Depends(get_session)):
    """Deleta paciente (soft delete)."""
    patient = session.get(Patient, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Paciente não encontrado")
    
    PatientRepository.update(session, patient_id, {"active": False})
    logger.info(f"Paciente desativado: {patient.name}")




