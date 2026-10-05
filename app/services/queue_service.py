
from datetime import date, datetime, timezone, timedelta
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.queue_entry import QueueEntry
from app.models.queue_control import DoctorQueueControl
from app.models.emergency_case import EmergencyCase
from app.models.appointment import Appointment
from app.repositories.appointment_repository import AppointmentRepository
from app.repositories.queue_repository import QueueRepository
from app.services.audit_service import AuditService

class QueueService:
    def __init__(self):
        self.repo=QueueRepository(); self.appointments=AppointmentRepository()

    def _control(self,db,doctor_id):
        c=db.query(DoctorQueueControl).filter(DoctorQueueControl.doctor_id==doctor_id).first()
        if not c:
            c=DoctorQueueControl(doctor_id=doctor_id,is_paused=False); db.add(c); db.flush()
        return c

    def add_appointment_to_queue(self,db,appointment_id,user_id):
        appointment=self.appointments.get(db,appointment_id)
        if not appointment: raise HTTPException(404,"Appointment not found")
        if appointment.queue_entry: return appointment.queue_entry
        if appointment.status!="CHECKED_IN": raise HTTPException(400,"Appointment must be checked in before entering the queue")
        number=self.repo.next_number(db,appointment.doctor_id,date.today())
        entry=QueueEntry(appointment_id=appointment.id,patient_id=appointment.patient_id,doctor_id=appointment.doctor_id,queue_number=number,status="WAITING")
        appointment.status="IN_QUEUE"; result=self.repo.create(db,entry)
        AuditService.log("QUEUE_ENTRY_CREATED",user_id,queue_entry_id=result.id,appointment_id=appointment.id)
        return result

    def waiting(self,db,doctor_id): return self.repo.waiting(db,doctor_id)
    def active_queue(self,db,doctor_id): return self.repo.active_for_doctor(db,doctor_id)
    def patient_queue(self,db,patient_id): return self.repo.waiting_for_patient(db,patient_id)

    def set_paused(self,db,doctor_id,paused,reason=None,user_id=None):
        c=self._control(db,doctor_id); c.is_paused=paused; c.reason=reason if paused else None
        db.commit(); db.refresh(c)
        AuditService.log("QUEUE_PAUSED" if paused else "QUEUE_RESUMED",user_id,doctor_id=doctor_id,reason=reason)
        return c

    def control(self,db,doctor_id): 
        c=self._control(db,doctor_id); db.commit(); return c

    def call_next(self,db,doctor_id,user_id):
        c=self._control(db,doctor_id)
        if c.is_paused: raise HTTPException(409,"Queue is paused. Resolve the emergency before calling the next patient.")
        waiting=self.repo.waiting(db,doctor_id)
        if not waiting: raise HTTPException(404,"No waiting patients")
        entry=waiting[0]; entry.status="CALLED"; entry.called_at=datetime.now(timezone.utc).replace(tzinfo=None)
        if entry.appointment: entry.appointment.status="IN_CONSULTATION"
        db.commit(); db.refresh(entry)
        AuditService.log("PATIENT_CALLED",user_id,queue_entry_id=entry.id,patient_id=entry.patient_id)
        return entry

    def start_consultation(self,db,entry_id,user_id):
        entry=self.repo.get(db,entry_id)
        if not entry: raise HTTPException(404,"Queue entry not found")
        if entry.status!="CALLED": raise HTTPException(400,"Only called patients can start consultation")
        entry.status="IN_CONSULTATION"; db.commit(); db.refresh(entry); return entry

    def complete(self,db,entry_id,user_id):
        entry=self.repo.get(db,entry_id)
        if not entry: raise HTTPException(404,"Queue entry not found")
        if entry.status!="IN_CONSULTATION": raise HTTPException(400,"Patient is not in consultation")
        entry.status="COMPLETED"; entry.completed_at=datetime.utcnow()
        if entry.appointment: entry.appointment.status="COMPLETED"
        emergency=db.query(EmergencyCase).filter(EmergencyCase.appointment_id==entry.appointment_id,EmergencyCase.status=="ACTIVE").first() if entry.appointment_id else None
        if emergency:
            emergency.status="RESOLVED"; emergency.resolved_at=datetime.utcnow()
            self.set_paused(db,entry.doctor_id,False,None,user_id)
        db.commit(); db.refresh(entry)
        AuditService.log("QUEUE_COMPLETED",user_id,queue_entry_id=entry.id,patient_id=entry.patient_id)
        return entry

    def create_emergency(self,db,data,user_id):
        patient=db.get(__import__("app.models.patient",fromlist=["Patient"]).Patient,data.patient_id)
        doctor=db.get(__import__("app.models.doctor",fromlist=["Doctor"]).Doctor,data.doctor_id)
        if not patient: raise HTTPException(404,"Patient not found")
        if not doctor: raise HTTPException(404,"Doctor not found")
        now=datetime.now()
        end=(now+timedelta(minutes=30)).time()
        appointment=Appointment(patient_id=patient.id,doctor_id=doctor.id,appointment_date=now.date(),start_time=now.time().replace(second=0,microsecond=0),end_time=end,duration_minutes=30,appointment_type="EMERGENCY",reason=data.reason,created_by=user_id,status="IN_QUEUE")
        db.add(appointment); db.flush()
        number=self.repo.next_number(db,doctor.id,now.date())
        entry=QueueEntry(appointment_id=appointment.id,patient_id=patient.id,doctor_id=doctor.id,queue_number=number,status="CALLED")
        db.add(entry); db.flush()
        case=EmergencyCase(appointment_id=appointment.id,patient_id=patient.id,doctor_id=doctor.id,reason=data.reason,created_by=user_id)
        db.add(case)
        db.flush()
        self.set_paused(db,doctor.id,True,f"Emergency case #{case.id}: {data.reason}",user_id)
        db.commit(); db.refresh(entry)
        return entry
