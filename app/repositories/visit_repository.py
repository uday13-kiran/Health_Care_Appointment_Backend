from sqlalchemy.orm import Session

from app.models.visit import Visit


class VisitRepository:
    def get_by_appointment(self, db: Session, appointment_id: int):
        return db.query(Visit).filter(Visit.appointment_id == appointment_id).first()

    def create(self, db: Session, visit: Visit):
        db.add(visit)
        db.commit()
        db.refresh(visit)
        return visit
