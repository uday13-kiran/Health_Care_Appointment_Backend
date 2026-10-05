from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.patient import Patient


class PatientRepository:
    def get(self, db: Session, patient_id: int):
        return db.get(Patient, patient_id)

    def list(self, db: Session):
        return list(db.scalars(select(Patient).order_by(Patient.id.desc())))

    def create(self, db: Session, patient: Patient):
        db.add(patient)
        db.commit()
        db.refresh(patient)
        return patient
