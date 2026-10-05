from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.availability import DoctorAvailability


class AvailabilityRepository:
    def list_for_doctor(self, db: Session, doctor_id: int):
        return list(
            db.scalars(
                select(DoctorAvailability)
                .where(
                    DoctorAvailability.doctor_id == doctor_id,
                    DoctorAvailability.is_active.is_(True),
                )
                .order_by(DoctorAvailability.day_of_week)
            )
        )

    def create(self, db: Session, availability: DoctorAvailability):
        db.add(availability)
        db.commit()
        db.refresh(availability)
        return availability
