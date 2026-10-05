from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import require_roles
from app.permissions.roles import ADMIN, DOCTOR
from app.schemas.visit import VisitCreate, VisitResponse
from app.services.visit_service import VisitService

router = APIRouter(prefix="/visits", tags=["Visits"])
service = VisitService()


@router.post("/", response_model=VisitResponse)
def create_visit(
    data: VisitCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(ADMIN, DOCTOR)),
):
    doctor_id = (
        current_user.doctor.id
        if current_user.role.name == DOCTOR and current_user.doctor
        else None
    )

    if current_user.role.name == DOCTOR and doctor_id is None:
        from fastapi import HTTPException
        raise HTTPException(403, "Doctor profile not found")

    if current_user.role.name == ADMIN:
        appointment = service.appointments.get(db, data.appointment_id)
        doctor_id = appointment.doctor_id if appointment else None

    return service.create(db, data, doctor_id, current_user.id)


@router.post("/{visit_id}/complete", response_model=VisitResponse)
def complete_visit(
    visit_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(ADMIN, DOCTOR)),
):
    doctor_id = (
        current_user.doctor.id
        if current_user.role.name == DOCTOR and current_user.doctor
        else db.get(__import__("app.models.visit", fromlist=["Visit"]).Visit, visit_id).doctor_id
    )
    return service.complete(db, visit_id, doctor_id, current_user.id)
