from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Healthcare Appointment & Queue Management System"
    debug: bool = True

    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/healthcare_db"
    mongo_url: str = "mongodb://localhost:27017"
    mongo_db: str = "healthcare_audit"

    jwt_secret_key: str = "change-this-secret-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    cors_origins: str = "http://localhost:5174,http://127.0.0.1:5174,https://glistening-paprenjak-fed1c9.netlify.app"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
