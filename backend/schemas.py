from datetime import datetime
from typing import Optional, List
from pydantic import field_validator, BaseModel, EmailStr, Field, ValidationInfo
from pydantic import ConfigDict
from backend.enums import UserRole, AppointmentStatus

# ===== Responses (Leitura) =====

class RoomResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    capacity: int
    active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class PatientResponse(BaseModel):
    id: int
    name: str
    birthdate: Optional[datetime]
    email: Optional[str]
    notes: Optional[str]
    phone: Optional[str]
    is_child: bool
    active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: UserRole
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class AppointmentResponse(BaseModel):
    id: int
    start_dt: datetime
    end_dt: datetime
    status: AppointmentStatus
    notes: Optional[str]
    room: Optional[RoomResponse]
    patient: Optional[PatientResponse]
    student: Optional[UserResponse]
    supervisor: Optional[UserResponse]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class AppointmentListResponse(BaseModel):
    """Resposta simplificada para listas."""
    id: int
    start_dt: datetime
    end_dt: datetime
    status: AppointmentStatus
    room_name: Optional[str]
    patient_name: Optional[str]
    student_name: Optional[str]
    supervisor_name: Optional[str]

# ===== Requests (Criação/Atualização) =====

class RoomCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    capacity: int = Field(default=1, ge=1)

class RoomUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    capacity: Optional[int] = None
    active: Optional[bool] = None

class PatientCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    birthdate: Optional[datetime] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    notes: Optional[str] = None
    is_child: bool = False

class PatientUpdate(BaseModel):
    name: Optional[str] = None
    birthdate: Optional[datetime] = None
    email: Optional[EmailStr] = None
    notes: Optional[str] = None
    phone: Optional[str] = None
    is_child: Optional[bool] = None
    active: Optional[bool] = None

class UserCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    email: EmailStr
    password: str = Field(..., min_length=8)
    role: UserRole = UserRole.STUDENT

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None

class AppointmentCreate(BaseModel):
    start_dt: datetime
    end_dt: datetime
    room_id: int
    patient_id: int
    student_id: int
    supervisor_id: int
    notes: Optional[str] = None

    @field_validator('end_dt')
    def end_dt_after_start_dt(cls, v, info: ValidationInfo):
        # Pydantic v2: info.data é um dict com os outros campos
        start_dt = None
        if hasattr(info, 'data') and isinstance(info.data, dict):
            start_dt = info.data.get('start_dt')
        if start_dt is not None and v <= start_dt:
            raise ValueError('end_dt deve ser posterior a start_dt')
        return v

class AppointmentUpdate(BaseModel):
    status: Optional[AppointmentStatus] = None
    notes: Optional[str] = None

# ===== API Responses (genéricas) =====

class APIResponse(BaseModel):
    """Resposta genérica da API."""
    success: bool
    message: str
    data: Optional[dict] = None

class ErrorDetail(BaseModel):
    field: str
    message: str

class ValidationErrorResponse(BaseModel):
    """Resposta de erro de validação."""
    success: bool = False
    message: str
    errors: List[ErrorDetail]

# ===== Auth =====

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)



