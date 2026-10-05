
from datetime import date, time
from pydantic import BaseModel, ConfigDict

class LeaveCreate(BaseModel):
    leave_date: date
    start_time: time | None = None
    end_time: time | None = None
    reason: str | None = None

class LeaveResponse(LeaveCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    doctor_id: int
    approval_status: str

class LeaveApproval(BaseModel):
    approval_status: str
