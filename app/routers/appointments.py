
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user, require_roles
from app.permissions.roles import ADMIN, DOCTOR, PATIENT, RECEPTIONIST
from app.schemas.appointment import AppointmentCreate, AppointmentResponse
from app.services.appointment_service import AppointmentService

router=APIRouter(prefix="/appointments",tags=["Appointments"]); service=AppointmentService()

@router.post("/",response_model=AppointmentResponse)
def create_appointment(data:AppointmentCreate,db:Session=Depends(get_db),current_user=Depends(require_roles(ADMIN,PATIENT,RECEPTIONIST))):
    if current_user.role.name==PATIENT and (not current_user.patient or current_user.patient.id!=data.patient_id):
        raise HTTPException(403,"Patients can only book for themselves")
    return service.create(db,data,current_user.id)

@router.get("/",response_model=list[AppointmentResponse])
def list_appointments(appointment_date:str|None=None,db:Session=Depends(get_db),current_user=Depends(require_roles(ADMIN,DOCTOR,RECEPTIONIST))):
    from datetime import date
    parsed=date.fromisoformat(appointment_date) if appointment_date else None
    if current_user.role.name==DOCTOR:
        return service.doctor_appointments(db,current_user.doctor.id,parsed) if current_user.doctor else []
    return service.list_all(db,parsed)

@router.get("/doctor/{doctor_id}",response_model=list[AppointmentResponse])
def doctor_appointments(doctor_id:int,appointment_date:str|None=None,db:Session=Depends(get_db),current_user=Depends(require_roles(ADMIN,DOCTOR,RECEPTIONIST,PATIENT))):
    from datetime import date
    parsed=date.fromisoformat(appointment_date) if appointment_date else None
    if current_user.role.name==DOCTOR and (not current_user.doctor or current_user.doctor.id!=doctor_id): raise HTTPException(403,"You can only access your own appointments")
    return service.doctor_appointments(db,doctor_id,parsed)

@router.get("/patient/{patient_id}",response_model=list[AppointmentResponse])
def patient_appointments(patient_id:int,db:Session=Depends(get_db),current_user=Depends(get_current_user)):
    if current_user.role.name==PATIENT and (not current_user.patient or current_user.patient.id!=patient_id): raise HTTPException(403,"You can only access your own appointments")
    return service.patient_appointments(db,patient_id)

@router.get("/{appointment_id}",response_model=AppointmentResponse)
def get_appointment(appointment_id:int,db:Session=Depends(get_db),current_user=Depends(get_current_user)):
    appointment=service.get(db,appointment_id)
    if current_user.role.name==PATIENT and (not current_user.patient or current_user.patient.id!=appointment.patient_id): raise HTTPException(403,"You can only access your own appointment")
    if current_user.role.name==DOCTOR and (not current_user.doctor or current_user.doctor.id!=appointment.doctor_id): raise HTTPException(403,"You can only access your own appointments")
    return appointment

@router.post("/{appointment_id}/cancel",response_model=AppointmentResponse)
def cancel(appointment_id:int,db:Session=Depends(get_db),current_user=Depends(require_roles(ADMIN,PATIENT,RECEPTIONIST))):
    appointment=service.get(db,appointment_id)
    if current_user.role.name==PATIENT and (not current_user.patient or current_user.patient.id!=appointment.patient_id): raise HTTPException(403,"You can only cancel your own appointment")
    return service.cancel(db,appointment_id,current_user.id)

@router.post("/{appointment_id}/check-in",response_model=AppointmentResponse)
def check_in(appointment_id:int,db:Session=Depends(get_db),current_user=Depends(require_roles(ADMIN,RECEPTIONIST))):
    return service.check_in(db,appointment_id,current_user.id)
