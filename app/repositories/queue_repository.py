from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.queue_entry import QueueEntry


class QueueRepository:
    def next_number(self, db: Session, doctor_id: int, arrival_date):
        count = db.scalar(
            select(func.count())
            .select_from(QueueEntry)
            .where(
                QueueEntry.doctor_id == doctor_id,
                func.date(QueueEntry.arrival_time) == arrival_date,
            )
        )
        return (count or 0) + 1

    def create(self, db: Session, entry: QueueEntry):
        db.add(entry)
        db.commit()
        db.refresh(entry)
        return entry

    def waiting(self, db: Session, doctor_id: int):
        return list(
            db.scalars(
                select(QueueEntry)
                .where(
                    QueueEntry.doctor_id == doctor_id,
                    QueueEntry.status == "WAITING",
                )
                .order_by(QueueEntry.arrival_time)
            )
        )

    def active_for_doctor(self, db: Session, doctor_id: int):
        return list(
            db.scalars(
                select(QueueEntry)
                .where(
                    QueueEntry.doctor_id == doctor_id,
                    QueueEntry.status.in_(
                        ["WAITING", "CALLED", "IN_CONSULTATION"]
                    ),
                )
                .order_by(QueueEntry.arrival_time)
            )
        )

    def waiting_for_patient(self, db: Session, patient_id: int):
        return list(
            db.scalars(
                select(QueueEntry)
                .where(
                    QueueEntry.patient_id == patient_id,
                    QueueEntry.status.in_(["WAITING", "CALLED", "IN_CONSULTATION"]),
                )
                .order_by(QueueEntry.arrival_time.desc())
            )
        )

    def get(self, db: Session, entry_id: int):
        return db.get(QueueEntry, entry_id)
