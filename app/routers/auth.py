from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.schemas.auth import (
    DoctorRegisterRequest,
    LoginRequest,
    MeResponse,
    PatientRegisterRequest,
    RegistrationResponse,
    TokenResponse,
)
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])
service = AuthService()


@router.post("/register/patient", response_model=RegistrationResponse, status_code=201)
def register_patient(data: PatientRegisterRequest, db: Session = Depends(get_db)):
    user, patient = service.register_patient(db, data)
    return {
        "id": user.id,
        "email": user.email,
        "role": "PATIENT",
        "profile_id": patient.id,
        "profile_code": patient.patient_code,
        "message": "Patient account created successfully. You can now sign in.",
    }


@router.post("/register/doctor", response_model=RegistrationResponse, status_code=201)
def register_doctor(data: DoctorRegisterRequest, db: Session = Depends(get_db)):
    user, doctor = service.register_doctor(db, data)
    return {
        "id": user.id,
        "email": user.email,
        "role": "DOCTOR",
        "profile_id": doctor.id,
        "profile_code": doctor.doctor_code,
        "message": "Doctor account created successfully. You can now sign in.",
    }


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    token = service.login(db, data.email, data.password, data.role)
    return {"access_token": token}


@router.get("/me", response_model=MeResponse)
def me(current_user=Depends(get_current_user)):
    profile_id = None
    if current_user.role.name == "PATIENT" and current_user.patient:
        profile_id = current_user.patient.id
    elif current_user.role.name == "DOCTOR" and current_user.doctor:
        profile_id = current_user.doctor.id

    return {
        "id": current_user.id,
        "email": current_user.email,
        "role": current_user.role.name,
        "profile_id": profile_id,
    }
