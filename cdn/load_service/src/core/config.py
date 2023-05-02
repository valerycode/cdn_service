from pathlib import Path

from pydantic import BaseSettings, Field

BASE_DIR = Path(__file__).parent.parent
ENV_FILE = BASE_DIR.parent / ".env.local"


class Settings(BaseSettings):
    PROJECT_NAME: str = "S3 Load service"
    DEBUG: bool = Field(True, env="S3LS_DEBUG")
    CELERY_BROKER_URI: str = Field(..., env="S3LS_CELERY_BROKER_URI")
    CELERY_BACKEND_URI: str = Field(..., env="S3LS_CELERY_BACKEND_URI")
    STORAGE_BROKER_URI: str = Field(..., env="S3LS_STORAGE_BROKER_URI")
    HOME_STORAGE_URI: str = Field("localhost:9000", env="S3LS_HOME_STORAGE_URI")
    HOME_STORAGE_ID: str = Field("edge_test", env="S3LS_HOME_STORAGE_ID")
    SYNC_URI: str = Field(..., env="S3LS_SYNC_URI")
    HEARTBEAT_URI: str = Field(..., env="S3LS_HEARTBEAT_URI")
    BEAT_TIMEOUT: int = Field(30, env="BEAT_TIMEOUT")
    API_KEY: str = Field("secret", env="S3LS_API_KEY")
    BUCKET: str = "movies"
    ACCESS_KEY: str = Field(..., env="S3LS_ACCESS_KEY")
    SECRET_KEY: str = Field(..., env="S3LS_SECRET_KEY")


settings = Settings(_env_file=ENV_FILE)
