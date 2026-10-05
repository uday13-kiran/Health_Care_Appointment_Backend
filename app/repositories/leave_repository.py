
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.doctor_leave import DoctorLeave

class LeaveRepository:
    def for_date(self, db, doctor_id, leave_date):
        return list(db.scalars(select(DoctorLeave).where(DoctorLeave.doctor_id == doctor_id, DoctorLeave.leave_date == leave_date)))
    def create(self, db, leave):
        db.add(leave); db.commit(); db.refresh(leave); return leave
    def list_all(self, db, doctor_id=None):
        stmt=select(DoctorLeave)
        if doctor_id is not None: stmt=stmt.where(DoctorLeave.doctor_id == doctor_id)
        return list(db.scalars(stmt.order_by(DoctorLeave.leave_date.desc())))
    def get(self, db, leave_id): return db.get(DoctorLeave, leave_id)
