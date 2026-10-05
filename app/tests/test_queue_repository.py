from datetime import datetime, timedelta
from types import SimpleNamespace

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.core.database import Base
from app.main import app as application
from app.models.queue_entry import QueueEntry
from app.repositories.queue_repository import QueueRepository
from app.services.queue_service import QueueService


def test_adding_already_queued_appointment_returns_existing_entry():
    entry = object()
    appointment = SimpleNamespace(status="IN_QUEUE", queue_entry=entry)
    service = QueueService()
    service.appointments = SimpleNamespace(get=lambda db, appointment_id: appointment)

    result = service.add_appointment_to_queue(db=None, appointment_id=24, user_id=1)

    assert result is entry


def test_active_for_doctor_returns_active_entries_in_arrival_order():
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine, tables=[QueueEntry.__table__])
    now = datetime(2026, 1, 1, 9)

    with Session(engine) as db:
        db.add_all(
            [
                QueueEntry(
                    patient_id=1,
                    doctor_id=10,
                    queue_number=2,
                    status="CALLED",
                    arrival_time=now + timedelta(minutes=1),
                ),
                QueueEntry(
                    patient_id=2,
                    doctor_id=10,
                    queue_number=1,
                    status="WAITING",
                    arrival_time=now,
                ),
                QueueEntry(
                    patient_id=3,
                    doctor_id=10,
                    queue_number=3,
                    status="COMPLETED",
                    arrival_time=now + timedelta(minutes=2),
                ),
                QueueEntry(
                    patient_id=4,
                    doctor_id=11,
                    queue_number=1,
                    status="WAITING",
                    arrival_time=now,
                ),
                QueueEntry(
                    patient_id=5,
                    doctor_id=10,
                    queue_number=4,
                    status="IN_CONSULTATION",
                    arrival_time=now + timedelta(minutes=3),
                ),
            ]
        )
        db.commit()

        active = QueueRepository().active_for_doctor(db, doctor_id=10)

    assert [entry.status for entry in active] == [
        "WAITING",
        "CALLED",
        "IN_CONSULTATION",
    ]
    paths = application.openapi()["paths"]
    assert "/api/v1/queue/doctor/{doctor_id}/active" in paths
    assert "/api/v1/queue/my" in paths
