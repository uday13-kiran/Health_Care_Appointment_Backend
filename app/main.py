from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import Base, engine
from sqlalchemy import text
from app.routers import (
    admin,
    appointments,
    auth,
    availability,
    doctor_leave,
    doctors,
    patients,
    queue,
    reports,
    visits,
)

# Import models so SQLAlchemy knows all tables.
from app.models import appointment, availability as availability_model
from app.models import doctor, doctor_leave as leave_model
from app.models import patient, queue_entry, role, user, visit
from app.models import doctor_break, queue_control, emergency_case


app = FastAPI(title=settings.app_name, debug=settings.debug)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)
    # The project intentionally does not use Alembic. Keep this tiny compatibility
    # patch so existing databases gain the new leave approval field safely.
    with engine.begin() as conn:
        conn.execute(text(
            "ALTER TABLE doctor_leaves ADD COLUMN IF NOT EXISTS approval_status VARCHAR(20) DEFAULT 'PENDING'"
        ))
        conn.execute(text(
            "UPDATE doctor_leaves SET approval_status = 'APPROVED' WHERE approval_status IS NULL"
        ))


@app.get("/health", tags=["Health"])
def health():
    return JSONResponse({"status": "ok"})


app.include_router(auth.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1")
app.include_router(patients.router, prefix="/api/v1")
app.include_router(doctors.router, prefix="/api/v1")
app.include_router(availability.router, prefix="/api/v1")
app.include_router(doctor_leave.router, prefix="/api/v1")
app.include_router(appointments.router, prefix="/api/v1")
app.include_router(queue.router, prefix="/api/v1")
app.include_router(visits.router, prefix="/api/v1")
app.include_router(reports.router, prefix="/api/v1")
