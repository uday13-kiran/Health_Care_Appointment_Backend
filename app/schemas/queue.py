
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class QueueEntryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    appointment_id: int | None
    patient_id: int
    patient_name: str | None = None
    doctor_id: int
    doctor_name: str | None = None
    queue_number: int
    status: str
    arrival_time: datetime

class WaitTimeResponse(BaseModel):
    doctor_id: int
    queue_number: int
    estimated_wait_minutes: int

class QueueControlRequest(BaseModel):
    reason: str | None = None

class QueueControlResponse(BaseModel):
    doctor_id: int
    is_paused: bool
    reason: str | None = None

class EmergencyCreate(BaseModel):
    patient_id: int
    doctor_id: int
    reason: str
