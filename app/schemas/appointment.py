
from datetime import date, time
from pydantic import BaseModel, ConfigDict

class AppointmentCreate(BaseModel):
    patient_id: int
    doctor_id: int
    appointment_date: date
    start_time: time | None = None
    duration_minutes: int = 30
    reason: str | None = None
    appointment_type: str = "SCHEDULED"

class AppointmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    patient_id: int
    patient_name: str | None = None
    doctor_id: int
    doctor_name: str | None = None
    appointment_date: date
    start_time: time
    end_time: time
    duration_minutes: int
    status: str
    appointment_type: str
    reason: str | None
