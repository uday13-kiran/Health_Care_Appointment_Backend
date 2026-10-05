from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.appointment import Appointment


ACTIVE_STATUSES = {
    "SCHEDULED",
    "CHECKED_IN",
    "IN_QUEUE",
    "IN_CONSULTATION",
}


class AppointmentRepository:
    def get(self, db: Session, appointment_id: int):
        return db.get(Appointment, appointment_id)

    def list_all(self, db: Session, appointment_date=None):
        stmt = select(Appointment)
        if appointment_date:
            stmt = stmt.where(Appointment.appointment_date == appointment_date)
        return list(db.scalars(stmt.order_by(Appointment.appointment_date.desc(), Appointment.start_time)))

    def list_for_patient(self, db: Session, patient_id: int):
        return list(
            db.scalars(
                select(Appointment)
                .where(Appointment.patient_id == patient_id)
                .order_by(Appointment.appointment_date.desc(), Appointment.start_time)
            )
        )

    def list_for_doctor(self, db: Session, doctor_id: int, appointment_date=None):
        stmt = select(Appointment).where(Appointment.doctor_id == doctor_id)
        if appointment_date:
            stmt = stmt.where(Appointment.appointment_date == appointment_date)
        return list(db.scalars(stmt.order_by(Appointment.start_time)))

    def find_overlaps(self, db: Session, doctor_id, appointment_date, start_time, end_time):
        appointments = db.scalars(
            select(Appointment).where(
                Appointment.doctor_id == doctor_id,
                Appointment.appointment_date == appointment_date,
                Appointment.status.in_(ACTIVE_STATUSES),
            )
        )
        return [
            a for a in appointments
            if start_time < a.end_time and end_time > a.start_time
        ]

    def create(self, db: Session, appointment: Appointment):
        db.add(appointment)
        db.commit()
        db.refresh(appointment)
        return appointment
