from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.models.role import Role
from app.models.user import User
from app.models.patient import Patient
from app.models.doctor import Doctor
from app.permissions.roles import ALL_ROLES
from app.repositories.user_repository import UserRepository


class AuthService:
    def __init__(self):
        self.users = UserRepository()

    def login(self, db: Session, email: str, password: str, selected_role: str):
        selected_role = selected_role.upper()

        if selected_role not in ALL_ROLES:
            raise HTTPException(400, "Invalid role")

        user = self.users.get_by_email(db, email)
        if not user or not verify_password(password, user.password_hash):
            raise HTTPException(401, "Invalid email or password")

        if user.role.name != selected_role:
            raise HTTPException(403, "Selected role does not match your account role")

        token = create_access_token(user.id, user.role.name)
        return token

    def register_patient(self, db: Session, data):
        if self.users.get_by_email(db, data.email):
            raise HTTPException(409, "Email already exists")

        role = db.scalar(select(Role).where(Role.name == "PATIENT"))
        if not role:
            raise HTTPException(500, "PATIENT role is not configured")

        user = User(
            email=data.email,
            password_hash=hash_password(data.password),
            role_id=role.id,
        )
        db.add(user)
        db.flush()

        count = db.query(Patient).count() + 1
        patient = Patient(
            user_id=user.id,
            patient_code=f"PAT-{count:05d}",
            first_name=data.first_name,
            last_name=data.last_name,
            date_of_birth=data.date_of_birth,
            gender=data.gender,
            phone=data.phone,
            email=data.email,
            address=data.address,
        )
        db.add(patient)
        db.commit()
        db.refresh(user)
        db.refresh(patient)
        return user, patient

    def register_doctor(self, db: Session, data):
        if self.users.get_by_email(db, data.email):
            raise HTTPException(409, "Email already exists")

        if data.license_number:
            existing_license = db.scalar(select(Doctor).where(Doctor.license_number == data.license_number))
            if existing_license:
                raise HTTPException(409, "License number already exists")

        role = db.scalar(select(Role).where(Role.name == "DOCTOR"))
        if not role:
            raise HTTPException(500, "DOCTOR role is not configured")

        user = User(
            email=data.email,
            password_hash=hash_password(data.password),
            role_id=role.id,
        )
        db.add(user)
        db.flush()

        count = db.query(Doctor).count() + 1
        doctor = Doctor(
            user_id=user.id,
            doctor_code=f"DOC-{count:05d}",
            first_name=data.first_name,
            last_name=data.last_name,
            specialization=data.specialization,
            license_number=data.license_number,
            phone=data.phone,
            email=data.email,
            status="ACTIVE",
        )
        db.add(doctor)
        db.commit()
        db.refresh(user)
        db.refresh(doctor)
        return user, doctor

    def create_user(self, db: Session, email: str, password: str, role_name: str):
        role = db.scalar(select(Role).where(Role.name == role_name.upper()))
        if not role:
            raise HTTPException(400, "Invalid role")

        if self.users.get_by_email(db, email):
            raise HTTPException(409, "Email already exists")

        user = User(
            email=email,
            password_hash=hash_password(password),
            role_id=role.id,
        )
        return self.users.create(db, user)
