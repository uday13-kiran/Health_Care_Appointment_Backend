from datetime import date

from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    role: str


class PatientRegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)
    first_name: str = Field(min_length=1, max_length=80)
    last_name: str = Field(min_length=1, max_length=80)
    date_of_birth: date | None = None
    gender: str | None = None
    phone: str | None = None
    address: str | None = None


class DoctorRegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)
    first_name: str = Field(min_length=1, max_length=80)
    last_name: str = Field(min_length=1, max_length=80)
    specialization: str = Field(min_length=1, max_length=100)
    license_number: str | None = None
    phone: str | None = None


class RegistrationResponse(BaseModel):
    id: int
    email: EmailStr
    role: str
    profile_id: int
    profile_code: str
    message: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class MeResponse(BaseModel):
    id: int
    email: EmailStr
    role: str
    profile_id: int | None = None
