from pydantic import BaseModel


class VisitCreate(BaseModel):
    appointment_id: int
    diagnosis: str | None = None
    notes: str | None = None
    prescription: str | None = None


class VisitResponse(BaseModel):
    id: int
    appointment_id: int
    doctor_id: int
    patient_id: int
    status: str
    diagnosis: str | None
    notes: str | None
    prescription: str | None
