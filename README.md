# Healthcare Appointment & Queue Management System

Simple FastAPI backend for:

- Admin
- Doctor
- Patient
- Receptionist

## Stack

- Python
- FastAPI
- SQLAlchemy
- PostgreSQL
- MongoDB
- JWT
- Pytest

## Architecture

Frontend
→ FastAPI routers
→ Authentication/RBAC
→ Services
→ Repositories
→ PostgreSQL

Audit events are stored in MongoDB.

## Run locally

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it and install:

```bash
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and update values if needed.

Start PostgreSQL and MongoDB, then:

```bash
uvicorn app.main:app --reload
```

Open:

http://localhost:8000/docs

## Frontend integration updates

The current backend supports the complete self-registration and live queue hand-off used by the HealthCare frontend.

### Self-registration

- `POST /api/v1/auth/register/patient` creates a PATIENT user and linked patient profile.
- `POST /api/v1/auth/register/doctor` creates a DOCTOR user and linked doctor profile.
- `GET /api/v1/auth/me` returns `profile_id` for patient and doctor accounts.

Admin and receptionist accounts remain admin-managed through `POST /api/v1/admin/users`.

### Appointment -> queue workflow

The intended live workflow is:

```text
Book appointment
      ↓
SCHEDULED
      ↓
Check in
      ↓
CHECKED_IN → queue entry is created automatically
      ↓
WAITING
      ↓
Call next
      ↓
CALLED
      ↓
Start consultation
      ↓
IN_CONSULTATION
      ↓
Complete
      ↓
COMPLETED
```

`POST /api/v1/queue/appointment/{appointment_id}` requires the appointment to be `CHECKED_IN` before creating a queue entry. Check-in creates that entry automatically; repeating the queue-add request returns the existing entry instead of failing.

Additional read endpoints used by the frontend:

- `GET /api/v1/appointments/`
- `GET /api/v1/appointments/doctor/{doctor_id}`
- `GET /api/v1/queue/my` — doctor-only active queue for the logged-in doctor (no doctor ID needed)
- `GET /api/v1/queue/doctor/{doctor_id}/active` — active queue entries in arrival order (`WAITING`, `CALLED`, `IN_CONSULTATION`)
- `GET /api/v1/queue/doctor/{doctor_id}` — waiting entries only; used by the call-next flow
- `GET /api/v1/queue/patient/{patient_id}`

Doctors should load their own queue with `GET /api/v1/queue/my`, call the next patient with `POST /api/v1/queue/doctor/{doctor_id}/call-next`, then start and complete only their own queue entries using `POST /api/v1/queue/{entry_id}/start` and `POST /api/v1/queue/{entry_id}/complete`.

### CORS

CORS is controlled through the `CORS_ORIGINS` environment variable as a comma-separated list.

Local development default:

```env
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

For deployment, set it to the exact frontend origin(s), for example:

```env
CORS_ORIGINS=https://your-frontend.example.com
```


## Release behavior updates

### Patient
- Booking requires only doctor + date; the backend automatically chooses the first available 30-minute slot.
- Patient appointment list hides internal IDs and the patient column.
- Patient can cancel only their own appointments.
- Patient cannot check in or add themselves to a queue.
- Patient queue is read-only status information.
- A patient can open a doctor profile and book directly from that doctor.

### Doctor
- Queue endpoint is restricted to the logged-in doctor's own queue.
- Appointment and queue responses expose patient/doctor names instead of requiring frontend ID lookups.
- Admin controls recurring doctor working hours.
- Doctor can add only their own breaks; a break cannot exceed 45 minutes.
- Doctor leave is submitted as PENDING and must be approved by an admin.
- Consultation is a clinical documentation step after queue/call flow, not an appointment-booking screen.

### Admin / Receptionist
- Only Admin/Receptionist can check patients in and place appointments into the live queue.
- Admin dashboard exposes today's care-flow analytics.
- Admin/Receptionist can pause/resume a doctor's queue.
- Admin/Receptionist can create an emergency case, assign it to a doctor, and automatically pause that doctor's normal queue until the emergency is completed.

### Database compatibility
This project intentionally does not add Alembic. New tables are created by `Base.metadata.create_all()`. The leave approval column is added with a small PostgreSQL startup compatibility patch for existing databases.
