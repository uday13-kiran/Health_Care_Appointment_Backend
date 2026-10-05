from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.doctor import Doctor


class DoctorRepository:
    def get(self, db: Session, doctor_id: int):
        return db.get(Doctor, doctor_id)

    def list(self, db: Session, specialization: str | None = None):
        stmt = select(Doctor).where(Doctor.status == "ACTIVE")
        if specialization:
            stmt = stmt.where(Doctor.specialization.ilike(f"%{specialization}%"))
        return list(db.scalars(stmt.order_by(Doctor.id)))

    def create(self, db: Session, doctor: Doctor):
        db.add(doctor)
        db.commit()
        db.refresh(doctor)
        return doctor
