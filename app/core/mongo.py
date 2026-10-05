from pymongo import MongoClient

from app.core.config import settings


mongo_client = MongoClient(settings.mongo_url)
mongo_db = mongo_client[settings.mongo_db]
audit_collection = mongo_db["audit_logs"]
