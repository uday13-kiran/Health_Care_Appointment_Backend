from pydantic import BaseModel, EmailStr


class DoctorCreate(BaseModel):
    first_name: str
    last_name: str
    specialization: str
    license_number: str | None = None
    phone: str | None = None
    email: EmailStr | None = None


class DoctorResponse(DoctorCreate):
    id: int
    doctor_code: str
    status: str
