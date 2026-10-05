from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.patient import Patient
from app.repositories.patient_repository import PatientRepository
from app.services.audit_service import AuditService


class PatientService:
    def __init__(self):
        self.repo = PatientRepository()

    def create(self, db: Session, data, user_id=None):
        code = f"PAT-{db.query(Patient).count() + 1:05d}"
        patient = Patient(patient_code=code, **data.model_dump())
        result = self.repo.create(db, patient)
        AuditService.log("PATIENT_REGISTERED", user_id, patient_id=result.id)
        return result

    def get(self, db: Session, patient_id: int):
        patient = self.repo.get(db, patient_id)
        if not patient:
            raise HTTPException(404, "Patient not found")
        return patient

    def list(self, db: Session):
        return self.repo.list(db)
