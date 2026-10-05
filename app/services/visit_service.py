from datetime import datetime
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.visit import Visit
from app.repositories.appointment_repository import AppointmentRepository
from app.repositories.visit_repository import VisitRepository
from app.services.audit_service import AuditService


class VisitService:
    def __init__(self):
        self.repo = VisitRepository()
        self.appointments = AppointmentRepository()

    def create(self, db: Session, data, doctor_id: int, user_id: int):
        appointment = self.appointments.get(db, data.appointment_id)

        if not appointment:
            raise HTTPException(404, "Appointment not found")
        if appointment.doctor_id != doctor_id:
            raise HTTPException(403, "You can only manage your own patients")
        if appointment.status not in {"IN_CONSULTATION", "IN_QUEUE"}:
            raise HTTPException(400, "Appointment is not ready for consultation")

        existing = self.repo.get_by_appointment(db, appointment.id)
        if existing:
            return existing

        visit = Visit(
            appointment_id=appointment.id,
            doctor_id=appointment.doctor_id,
            patient_id=appointment.patient_id,
            diagnosis=data.diagnosis,
            notes=data.notes,
            prescription=data.prescription,
        )
        appointment.status = "IN_CONSULTATION"
        result = self.repo.create(db, visit)

        AuditService.log(
            "CONSULTATION_STARTED",
            user_id,
            visit_id=result.id,
            appointment_id=appointment.id,
        )
        return result

    def complete(self, db: Session, visit_id: int, doctor_id: int, user_id: int):
        visit = db.get(Visit, visit_id)
        if not visit:
            raise HTTPException(404, "Visit not found")
        if visit.doctor_id != doctor_id:
            raise HTTPException(403, "You can only manage your own visits")

        visit.status = "COMPLETED"
        visit.ended_at = datetime.utcnow()
        visit.appointment.status = "COMPLETED"

        if visit.appointment.queue_entry:
            visit.appointment.queue_entry.status = "COMPLETED"
            visit.appointment.queue_entry.completed_at = datetime.utcnow()

        db.commit()
        db.refresh(visit)

        AuditService.log(
            "CONSULTATION_COMPLETED",
            user_id,
            visit_id=visit.id,
            appointment_id=visit.appointment_id,
        )
        return visit
