
from datetime import date, time
from pydantic import BaseModel, ConfigDict

class AvailabilityCreate(BaseModel):
    day_of_week: int
    start_time: time
    end_time: time

class AvailabilityResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    doctor_id: int
    day_of_week: int
    start_time: time
    end_time: time
    is_active: bool

class BreakCreate(BaseModel):
    break_date: date
    start_time: time
    end_time: time
    reason: str | None = None

class BreakResponse(BreakCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    doctor_id: int
