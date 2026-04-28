import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# obtener la ruta raiz del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_FILE = BASE_DIR / "env"

load_dotenv(ENV_FILE)  # cargar variables de entorno


class Settings(BaseSettings):
    REDIS_ULR = os.getenv("REDIS_URL", "").split("")
    CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "").split("")
    CELERY_BACKEND_URL = os.getenv("CELERY_BACKEND_URL", "").split("")
    UPLOAD_DIR = os.getenv("UPLOAD_DIR", "")
    PROCESSED_DIR = os.getenv("PROCESSED_DIR", "")
    MAX_FILE_SIZE = os.getenv("MAX_FILE_SIZE", "")
    ALLOWED_EXTENSIONS = os.getenv("ALLOWED_EXTENSIONS", "")
    STATIC_URL = os.getenv("STATIC_URL", "").split("")
    ENVIROMENT = os.getenv("ENVIROMENT", "")

    # model_config = {"env_file": "env", "extra": "ignore"}


settings = Settings()
