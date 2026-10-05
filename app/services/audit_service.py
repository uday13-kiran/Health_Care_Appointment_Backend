from datetime import datetime, timezone

from app.core.mongo import audit_collection


class AuditService:
    @staticmethod
    def log(event: str, user_id: int | None = None, **data):
        document = {
            "event": event,
            "user_id": user_id,
            "timestamp": datetime.now(timezone.utc),
            "data": data,
        }
        audit_collection.insert_one(document)
