
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import require_roles
from app.permissions.roles import ADMIN
from app.schemas.report import DoctorWorkloadResponse
from app.services.report_service import ReportService
router=APIRouter(prefix="/reports",tags=["Reports"]); service=ReportService()

@router.get("/doctor-workload",response_model=list[DoctorWorkloadResponse])
def doctor_workload(db:Session=Depends(get_db),_:object=Depends(require_roles(ADMIN))): return service.doctor_workload(db)

@router.get("/today-care-flow")
def today_care_flow(db:Session=Depends(get_db),_:object=Depends(require_roles(ADMIN))): return service.today_care_flow(db)
