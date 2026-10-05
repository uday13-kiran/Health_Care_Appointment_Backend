from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class QueueEntry(Base):
    __tablename__ = "queue_entries"

    id: Mapped[int] = mapped_column(primary_key=True)
    appointment_id: Mapped[int | None] = mapped_column(
        ForeignKey("appointments.id"), unique=True
    )
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id"), nullable=False)
    doctor_id: Mapped[int] = mapped_column(ForeignKey("doctors.id"), nullable=False)
    queue_number: Mapped[int] = mapped_column(nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="WAITING", nullable=False)
    arrival_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    called_at: Mapped[datetime | None] = mapped_column(DateTime)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime)

    appointment = relationship("Appointment", back_populates="queue_entry")
    patient = relationship("Patient", back_populates="queue_entries")
    doctor = relationship("Doctor", back_populates="queue_entries")

    @property
    def patient_name(self):
        return f"{self.patient.first_name} {self.patient.last_name}" if self.patient else None

    @property
    def doctor_name(self):
        return f"{self.doctor.first_name} {self.doctor.last_name}" if self.doctor else None
