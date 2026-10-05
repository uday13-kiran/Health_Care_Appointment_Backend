
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.availability import DoctorAvailability
from app.models.doctor_break import DoctorBreak
from app.repositories.availability_repository import AvailabilityRepository
from app.repositories.doctor_repository import DoctorRepository
from app.services.audit_service import AuditService

class AvailabilityService:
    def __init__(self):
        self.repo=AvailabilityRepository(); self.doctors=DoctorRepository()

    def create(self, db, doctor_id, data, user_id=None):
        doctor=self.doctors.get(db, doctor_id)
        if not doctor: raise HTTPException(404,"Doctor not found")
        if data.day_of_week not in range(7): raise HTTPException(400,"day_of_week must be between 0 and 6")
        if data.start_time >= data.end_time: raise HTTPException(400,"Start time must be before end time")
        availability=DoctorAvailability(doctor_id=doctor_id, **data.model_dump())
        result=self.repo.create(db,availability)
        AuditService.log("AVAILABILITY_UPDATED",user_id,doctor_id=doctor_id,availability_id=result.id)
        return result

    def list(self,db,doctor_id): return self.repo.list_for_doctor(db,doctor_id)

    def create_break(self, db, doctor_id, data, user_id=None):
        if not self.doctors.get(db, doctor_id): raise HTTPException(404,"Doctor not found")
        if data.start_time >= data.end_time: raise HTTPException(400,"Break start must be before end")
        from datetime import datetime
        minutes=(datetime.combine(data.break_date,data.end_time)-datetime.combine(data.break_date,data.start_time)).total_seconds()/60
        if minutes > 45: raise HTTPException(400,"Doctor breaks cannot be longer than 45 minutes")
        br=DoctorBreak(doctor_id=doctor_id, **data.model_dump())
        db.add(br); db.commit(); db.refresh(br)
        AuditService.log("DOCTOR_BREAK_ADDED",user_id,doctor_id=doctor_id,break_id=br.id)
        return br

    def list_breaks(self,db,doctor_id): return list(db.query(DoctorBreak).filter(DoctorBreak.doctor_id==doctor_id).order_by(DoctorBreak.break_date,DoctorBreak.start_time).all())
