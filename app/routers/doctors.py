from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import require_roles
from app.permissions.roles import ADMIN, DOCTOR, PATIENT, RECEPTIONIST
from app.schemas.doctor import DoctorCreate, DoctorResponse
from app.services.doctor_service import DoctorService

router = APIRouter(prefix="/doctors", tags=["Doctors"])
service = DoctorService()


@router.post("/", response_model=DoctorResponse)
def create_doctor(
    data: DoctorCreate,
    db: Session = Depends(get_db),
    _: object = Depends(require_roles(ADMIN)),
):
    return service.create(db, data)


@router.get("/", response_model=list[DoctorResponse])
def list_doctors(
    specialization: str | None = None,
    db: Session = Depends(get_db),
    _: object = Depends(require_roles(ADMIN, DOCTOR, PATIENT, RECEPTIONIST)),
):
    return service.list(db, specialization)


@router.get("/{doctor_id}", response_model=DoctorResponse)
def get_doctor(
    doctor_id: int,
    db: Session = Depends(get_db),
    _: object = Depends(require_roles(ADMIN, DOCTOR, PATIENT, RECEPTIONIST)),
):
    return service.get(db, doctor_id)
