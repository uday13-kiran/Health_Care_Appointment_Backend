from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.queue_entry import QueueEntry
from app.repositories.queue_repository import QueueRepository


class WaitTimeEstimator:
    def __init__(self):
        self.repo = QueueRepository()
        self.average_minutes = 15

    def estimate(self, db: Session, doctor_id: int, queue_number: int):
        waiting = self.repo.waiting(db, doctor_id)
        ahead = [
            item for item in waiting
            if item.queue_number < queue_number
        ]

        if not ahead:
            return 0

        return len(ahead) * self.average_minutes
