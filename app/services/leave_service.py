
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.doctor_leave import DoctorLeave
from app.repositories.doctor_repository import DoctorRepository
from app.repositories.leave_repository import LeaveRepository

class LeaveService:
    def __init__(self):
        self.repo = LeaveRepository()
        self.doctors = DoctorRepository()

    def create(self, db, doctor_id, data):
        if not self.doctors.get(db, doctor_id):
            raise HTTPException(404, "Doctor not found")
        if data.start_time and data.end_time and data.start_time >= data.end_time:
            raise HTTPException(400, "Start time must be before end time")
        leave = DoctorLeave(doctor_id=doctor_id, approval_status="PENDING", **data.model_dump())
        return self.repo.create(db, leave)

    def list(self, db, doctor_id=None):
        return self.repo.list_all(db, doctor_id)

    def approve(self, db, leave_id, status):
        if status not in {"APPROVED", "REJECTED"}:
            raise HTTPException(400, "approval_status must be APPROVED or REJECTED")
        leave = self.repo.get(db, leave_id)
        if not leave: raise HTTPException(404, "Leave not found")
        leave.approval_status = status
        db.commit(); db.refresh(leave)
        return leave
