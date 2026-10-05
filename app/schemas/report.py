
from pydantic import BaseModel
class DoctorWorkloadResponse(BaseModel):
    doctor_id:int
    doctor_name:str
    total_appointments:int
    completed_appointments:int
    cancelled_appointments:int
