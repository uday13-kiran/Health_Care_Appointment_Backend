from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.doctor import Doctor
from app.repositories.doctor_repository import DoctorRepository


class DoctorService:
    def __init__(self):
        self.repo = DoctorRepository()

    def create(self, db: Session, data):
        code = f"DOC-{db.query(Doctor).count() + 1:05d}"
        doctor = Doctor(doctor_code=code, **data.model_dump())
        return self.repo.create(db, doctor)

    def get(self, db: Session, doctor_id: int):
        doctor = self.repo.get(db, doctor_id)
        if not doctor:
            raise HTTPException(404, "Doctor not found")
        return doctor

    def list(self, db: Session, specialization=None):
        return self.repo.list(db, specialization)
