from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_roles
from app.permissions.roles import ADMIN, PATIENT, RECEPTIONIST
from app.schemas.patient import PatientCreate, PatientResponse
from app.services.patient_service import PatientService

router = APIRouter(prefix="/patients", tags=["Patients"])
service = PatientService()


@router.post("/", response_model=PatientResponse)
def create_patient(
    data: PatientCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(ADMIN, PATIENT, RECEPTIONIST)),
):
    return service.create(db, data, current_user.id)


@router.get("/", response_model=list[PatientResponse])
def list_patients(
    db: Session = Depends(get_db),
    _: object = Depends(require_roles(ADMIN, RECEPTIONIST)),
):
    return service.list(db)


@router.get("/{patient_id}", response_model=PatientResponse)
def get_patient(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    patient = service.get(db, patient_id)

    if current_user.role.name == PATIENT:
        if not current_user.patient or current_user.patient.id != patient_id:
            from fastapi import HTTPException
            raise HTTPException(403, "You can only access your own profile")

    return patient
