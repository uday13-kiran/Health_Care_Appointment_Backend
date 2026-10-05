
from datetime import datetime, timedelta, time
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.appointment import Appointment
from app.repositories.appointment_repository import AppointmentRepository
from app.repositories.doctor_repository import DoctorRepository
from app.repositories.leave_repository import LeaveRepository
from app.repositories.patient_repository import PatientRepository
from app.repositories.availability_repository import AvailabilityRepository
from app.services.audit_service import AuditService
from app.services.queue_service import QueueService
from app.models.doctor_break import DoctorBreak

class AppointmentService:
    def __init__(self):
        self.repo = AppointmentRepository()
        self.patients = PatientRepository()
        self.doctors = DoctorRepository()
        self.leaves = LeaveRepository()
        self.availability = AvailabilityRepository()

    def _slot_available(self, db, doctor, appointment_date, start, duration):
        end = (datetime.combine(appointment_date, start) + timedelta(minutes=duration)).time()
        availability = [a for a in doctor.availability if a.is_active and a.day_of_week == appointment_date.weekday() and a.start_time <= start and a.end_time >= end]
        if not availability:
            return False, end, "outside availability"
        for leave in self.leaves.for_date(db, doctor.id, appointment_date):
            if getattr(leave, "approval_status", "APPROVED") != "APPROVED":
                continue
            leave_start = leave.start_time or time(0,0)
            leave_end = leave.end_time or time(23,59,59)
            if start < leave_end and end > leave_start:
                return False, end, "doctor leave"
        breaks = db.query(DoctorBreak).filter(DoctorBreak.doctor_id == doctor.id, DoctorBreak.break_date == appointment_date).all()
        for br in breaks:
            if start < br.end_time and end > br.start_time:
                return False, end, "doctor break"
        overlaps = self.repo.find_overlaps(db, doctor.id, appointment_date, start, end)
        if overlaps:
            return False, end, "existing appointment"
        return True, end, ""

    def _find_first_slot(self, db, doctor, appointment_date, duration):
        weekday_items = [a for a in doctor.availability if a.is_active and a.day_of_week == appointment_date.weekday()]
        for a in sorted(weekday_items, key=lambda x: x.start_time):
            current = datetime.combine(appointment_date, a.start_time)
            boundary = datetime.combine(appointment_date, a.end_time)
            while current + timedelta(minutes=duration) <= boundary:
                ok, _, _ = self._slot_available(db, doctor, appointment_date, current.time(), duration)
                if ok:
                    return current.time()
                current += timedelta(minutes=15)
        return None

    def create(self, db: Session, data, current_user_id: int):
        patient = self.patients.get(db, data.patient_id)
        doctor = self.doctors.get(db, data.doctor_id)
        if not patient: raise HTTPException(404, "Patient not found")
        if not doctor: raise HTTPException(404, "Doctor not found")
        if data.duration_minutes <= 0 or data.duration_minutes > 60:
            raise HTTPException(400, "Duration must be between 1 and 60 minutes")

        start = data.start_time or self._find_first_slot(db, doctor, data.appointment_date, data.duration_minutes)
        if not start:
            raise HTTPException(409, "No appointment slot is available for the selected doctor and date")
        ok, end, reason = self._slot_available(db, doctor, data.appointment_date, start, data.duration_minutes)
        if not ok:
            raise HTTPException(409, f"Selected appointment slot is unavailable: {reason}")

        appointment = Appointment(patient_id=data.patient_id, doctor_id=data.doctor_id, appointment_date=data.appointment_date,
            start_time=start, end_time=end, duration_minutes=data.duration_minutes, reason=data.reason,
            appointment_type=data.appointment_type, created_by=current_user_id)
        result = self.repo.create(db, appointment)
        AuditService.log("APPOINTMENT_BOOKED", current_user_id, appointment_id=result.id, patient_id=result.patient_id, doctor_id=result.doctor_id)
        return result

    def get(self, db, appointment_id):
        appointment = self.repo.get(db, appointment_id)
        if not appointment: raise HTTPException(404, "Appointment not found")
        return appointment

    def list_all(self, db, appointment_date=None): return self.repo.list_all(db, appointment_date)
    def doctor_appointments(self, db, doctor_id, appointment_date=None): return self.repo.list_for_doctor(db, doctor_id, appointment_date)
    def patient_appointments(self, db, patient_id): return self.repo.list_for_patient(db, patient_id)

    def cancel(self, db, appointment_id, user_id):
        appointment = self.get(db, appointment_id)
        if appointment.status in {"COMPLETED","CANCELLED"}: raise HTTPException(400, "Appointment cannot be cancelled")
        appointment.status="CANCELLED"; db.commit(); db.refresh(appointment)
        AuditService.log("APPOINTMENT_CANCELLED", user_id, appointment_id=appointment.id)
        return appointment

    def check_in(self, db, appointment_id, user_id):
        appointment=self.get(db, appointment_id)
        if appointment.status!="SCHEDULED": raise HTTPException(400, "Only scheduled appointments can be checked in")
        appointment.status="CHECKED_IN"
        AuditService.log("PATIENT_CHECKED_IN", user_id, appointment_id=appointment.id)
        QueueService().add_appointment_to_queue(db, appointment_id, user_id)
        db.refresh(appointment); return appointment
