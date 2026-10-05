
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import require_roles
from app.permissions.roles import ADMIN, DOCTOR, PATIENT, RECEPTIONIST
from app.schemas.queue import QueueEntryResponse, WaitTimeResponse, QueueControlRequest, QueueControlResponse, EmergencyCreate
from app.services.queue_service import QueueService
from app.services.wait_time_service import WaitTimeEstimator

router=APIRouter(prefix="/queue",tags=["Queue"]); service=QueueService(); estimator=WaitTimeEstimator()

@router.post("/appointment/{appointment_id}",response_model=QueueEntryResponse)
def add_to_queue(appointment_id:int,db:Session=Depends(get_db),current_user=Depends(require_roles(ADMIN,RECEPTIONIST))):
    return service.add_appointment_to_queue(db,appointment_id,current_user.id)

@router.get("/patient/{patient_id}",response_model=list[QueueEntryResponse])
def patient_queue(patient_id:int,db:Session=Depends(get_db),current_user=Depends(require_roles(ADMIN,PATIENT,RECEPTIONIST))):
    if current_user.role.name==PATIENT and (not current_user.patient or current_user.patient.id!=patient_id): raise HTTPException(403,"You can only access your own queue status")
    return service.patient_queue(db,patient_id)

@router.get("/doctor/{doctor_id}",response_model=list[QueueEntryResponse])
def waiting(doctor_id:int,db:Session=Depends(get_db),current_user=Depends(require_roles(ADMIN,DOCTOR,RECEPTIONIST))):
    if current_user.role.name==DOCTOR and (not current_user.doctor or current_user.doctor.id!=doctor_id): raise HTTPException(403,"Doctors can only access their own queue")
    return service.waiting(db,doctor_id)

@router.get("/doctor/{doctor_id}/active",response_model=list[QueueEntryResponse])
def active_queue(doctor_id:int,db:Session=Depends(get_db),current_user=Depends(require_roles(ADMIN,DOCTOR,RECEPTIONIST))):
    if current_user.role.name==DOCTOR and (not current_user.doctor or current_user.doctor.id!=doctor_id): raise HTTPException(403,"Doctors can only access their own queue")
    return service.active_queue(db,doctor_id)

@router.get("/my",response_model=list[QueueEntryResponse])
def my_queue(db:Session=Depends(get_db),current_user=Depends(require_roles(DOCTOR))):
    if not current_user.doctor:
        raise HTTPException(403,"Doctor profile is not linked to this account")
    return service.active_queue(db,current_user.doctor.id)

@router.get("/doctor/{doctor_id}/control",response_model=QueueControlResponse)
def control(doctor_id:int,db:Session=Depends(get_db),current_user=Depends(require_roles(ADMIN,DOCTOR,RECEPTIONIST))):
    if current_user.role.name==DOCTOR and (not current_user.doctor or current_user.doctor.id!=doctor_id): raise HTTPException(403,"Doctors can only access their own queue")
    return service.control(db,doctor_id)

@router.post("/doctor/{doctor_id}/pause",response_model=QueueControlResponse)
def pause(doctor_id:int,data:QueueControlRequest,db:Session=Depends(get_db),current_user=Depends(require_roles(ADMIN,RECEPTIONIST))):
    return service.set_paused(db,doctor_id,True,data.reason,current_user.id)

@router.post("/doctor/{doctor_id}/resume",response_model=QueueControlResponse)
def resume(doctor_id:int,db:Session=Depends(get_db),current_user=Depends(require_roles(ADMIN,RECEPTIONIST))):
    return service.set_paused(db,doctor_id,False,None,current_user.id)

@router.post("/emergency",response_model=QueueEntryResponse)
def emergency(data:EmergencyCreate,db:Session=Depends(get_db),current_user=Depends(require_roles(ADMIN,RECEPTIONIST))):
    return service.create_emergency(db,data,current_user.id)

@router.post("/doctor/{doctor_id}/call-next",response_model=QueueEntryResponse)
def call_next(doctor_id:int,db:Session=Depends(get_db),current_user=Depends(require_roles(ADMIN,DOCTOR,RECEPTIONIST))):
    if current_user.role.name==DOCTOR and (not current_user.doctor or current_user.doctor.id!=doctor_id): raise HTTPException(403,"Doctors can only manage their own queue")
    return service.call_next(db,doctor_id,current_user.id)

@router.post("/{entry_id}/start",response_model=QueueEntryResponse)
def start(entry_id:int,db:Session=Depends(get_db),current_user=Depends(require_roles(ADMIN,DOCTOR))):
    if current_user.role.name==DOCTOR:
        entry=service.repo.get(db,entry_id)
        if not entry: raise HTTPException(404,"Queue entry not found")
        if not current_user.doctor or entry.doctor_id!=current_user.doctor.id: raise HTTPException(403,"Doctors can only manage their own queue")
    return service.start_consultation(db,entry_id,current_user.id)

@router.post("/{entry_id}/complete",response_model=QueueEntryResponse)
def complete(entry_id:int,db:Session=Depends(get_db),current_user=Depends(require_roles(ADMIN,DOCTOR))):
    if current_user.role.name==DOCTOR:
        entry=service.repo.get(db,entry_id)
        if not entry: raise HTTPException(404,"Queue entry not found")
        if not current_user.doctor or entry.doctor_id!=current_user.doctor.id: raise HTTPException(403,"Doctors can only manage their own queue")
    return service.complete(db,entry_id,current_user.id)

@router.get("/doctor/{doctor_id}/wait-time",response_model=WaitTimeResponse)
def wait_time(doctor_id:int,queue_number:int,db:Session=Depends(get_db),current_user=Depends(require_roles(ADMIN,DOCTOR,PATIENT,RECEPTIONIST))):
    if current_user.role.name==DOCTOR and (not current_user.doctor or current_user.doctor.id!=doctor_id): raise HTTPException(403,"Doctors can only access their own queue")
    if current_user.role.name==PATIENT:
        own=service.patient_queue(db,current_user.patient.id if current_user.patient else -1)
        if not any(x.doctor_id==doctor_id and x.queue_number==queue_number for x in own): raise HTTPException(403,"You can only view your own queue")
    minutes=estimator.estimate(db,doctor_id,queue_number)
    return {"doctor_id":doctor_id,"queue_number":queue_number,"estimated_wait_minutes":minutes}
