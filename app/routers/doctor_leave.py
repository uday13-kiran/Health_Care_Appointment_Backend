
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import require_roles
from app.permissions.roles import ADMIN, DOCTOR
from app.schemas.doctor_leave import LeaveCreate, LeaveResponse, LeaveApproval
from app.services.leave_service import LeaveService

router=APIRouter(prefix="/leaves", tags=["Doctor Leave"])
service=LeaveService()

@router.post("/doctor/{doctor_id}", response_model=LeaveResponse)
def create_leave(doctor_id:int, data:LeaveCreate, db:Session=Depends(get_db), current_user=Depends(require_roles(ADMIN,DOCTOR))):
    if current_user.role.name == DOCTOR:
        if not current_user.doctor or current_user.doctor.id != doctor_id:
            raise HTTPException(403,"You can only request your own leave")
    return service.create(db, doctor_id, data)

@router.get("/", response_model=list[LeaveResponse])
def list_leaves(doctor_id:int|None=None, db:Session=Depends(get_db), current_user=Depends(require_roles(ADMIN,DOCTOR))):
    if current_user.role.name == DOCTOR:
        doctor_id = current_user.doctor.id if current_user.doctor else -1
    return service.list(db, doctor_id)

@router.post("/{leave_id}/approve", response_model=LeaveResponse)
def approve_leave(leave_id:int, data:LeaveApproval, db:Session=Depends(get_db), _:object=Depends(require_roles(ADMIN))):
    return service.approve(db, leave_id, data.approval_status.upper())
