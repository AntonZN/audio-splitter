import os
from functools import lru_cache
from typing import List, Optional, Dict, Any

from dotenv import load_dotenv
from pydantic import BaseSettings, validator, PostgresDsn

load_dotenv()


class Settings(BaseSettings):
    DEBUG: bool = True
    AUTH_TOKEN: str = "123"
    LOG_LEVEL: str = "DEBUG"
    MEDIA_URL: str = "http://localhost"
    STORAGE_FOLDER: str = os.path.join("/storage")
    UPLOAD_FOLDER: str = os.path.join(STORAGE_FOLDER, "uploads")
    STEMS_FOLDER: str = os.path.join(STORAGE_FOLDER, "stems")

    RABBITMQ_HOST: str = "rabbitmq"
    RABBITMQ_USERNAME: str
    RABBITMQ_PASSWORD: str
    RABBITMQ_ROUTING_KEY: str = "records"
    RABBITMQ_ROUTING_KEY_TTS: str = "tts"

    MODELS: List[str] = [
        "aerich.models",
        "app.models.records",
    ]

    POSTGRES_SCHEME: str = "postgres"
    POSTGRES_HOST: str = "127.0.0.1"
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_PORT: str

    DATABASE_URI: Optional[str] = None

    @validator("DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        postgres = PostgresDsn.build(
            scheme=values.get("POSTGRES_SCHEME"),
            user=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_HOST"),
            port=values.get("POSTGRES_PORT"),
            path=f"/{values.get('POSTGRES_DB') or ''}",
        )

        return postgres

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings():
    return Settings()
