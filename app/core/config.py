import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# obtener la ruta raiz del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_FILE = BASE_DIR / "env"

load_dotenv(ENV_FILE)  # cargar variables de entorno


class Settings(BaseSettings):
    REDIS_URL: str = os.getenv("REDIS_URL", "")
    CELERY_BROKER_URL: str = os.getenv("CELERY_BROKER_URL", "")
    CELERY_BACKEND_URL: str = os.getenv("CELERY_BACKEND_URL", "")
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "")
    PROCESSED_DIR: str = os.getenv("PROCESSED_DIR", "")
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", ""))
    ALLOWED_EXTENSIONS: str = os.getenv("ALLOWED_EXTENSIONS", "")
    STATIC_URL: str = os.getenv("STATIC_URL", "")
    ENVIROMENT: str = os.getenv("ENVIROMENT", "")

    # model_config = {"env_file": "env", "extra": "ignore"}


settings = Settings()
