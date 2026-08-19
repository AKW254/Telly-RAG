from pathlib import Path
from typing import List, Dict, Any

from pydantic import field_validator
from pydantic_settings import BaseSettings,SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[2]
ENV_FILE = BASE_DIR / ".env"

class Settings(BaseSettings):
    # ============= APP SETTINGS =============
    app_name: str = "Telly RAG"
    app_version: str = "1.0.0"
    environment: str = "development"  # development, staging, production
    debug: bool = False
    
    #=============  LOGGER ===================
    LOG_LEVEL: str = "INFO"
    
    #=============  SECURITY ===================
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    
    #============= CORS  ===================
    cors_origins: List[str]
    cors_allow_credentials:bool = True
    cors_allow_methods: List[str] = ["*"]
    cors_allow_header: List[str] = ["*"]
    
    # ============= DATABASE =============
    db_host: str
    db_port: int
    db_name: str
    db_user: str
    db_password: str
    db_echo: bool = False
    
    #=============AI API KEY ================
    openrouter_api_key: str
    openrouter_base_url: str
    openrouter_model_name: str
    
    #===========lANGSMITH ===================
    langsmith_tracing: bool = True
    langsmith_endpoint: str
    langsmith_api_key: str
    langsmith_project: str
    
    #=============  Celery ===================
    celery_broker_url: str | None = None
    celery_result_backend: str | None = None
    celery_task_always_eager: bool | None = None
    celery_broker_connection_timeout: int = 5
    celery_broker_connection_max_retries: int = 1
    celery_timezone:str
    
    # ============= EMAIL SETTINGS =============
    email_host: str | None = None
    email_port: int = 587
    email_user: str | None = None
    email_pass: str | None = None
    email_from: str | None = None
    email_from_name: str = "Telly RAG"
    email_enabled: bool = True
    email_templates_dir: Path = BASE_DIR / "app" / "mailer" / "templates"
    
    # ============= DOCUMENTS STORAGE =============
    documents_dir: Path = BASE_DIR / "documents"
    
    # ============= loads settings from .env file and validates them =============
    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        extra="ignore",
        case_sensitive=False
    )

    @field_validator("debug", mode="before")
    @classmethod
    def _parse_debug_value(cls, value):
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in {"1", "true", "yes", "y", "on", "debug"}:
                return True
            if normalized in {"0", "false", "no", "n", "off", "release", "prod", "production"}:
                return False
        return value

    @field_validator("celery_broker_url", "celery_result_backend", mode="before")
    @classmethod
    def _normalize_celery_url(cls, value):
        if value is None:
            return None

        if not isinstance(value, str):
            return value

        normalized = value.strip().strip('"').strip("'")
        if not normalized:
            return None

        # Allow URLs copied directly from the redis CLI command.
        if normalized.startswith("redis-cli -u "):
            normalized = normalized.split("redis-cli -u ", maxsplit=1)[1].strip()

        return normalized

    def get_cors_origins(self) -> List[str]:
        """Parse CORS origins from string or return list"""
        if isinstance(self.cors_origins, str):
            return [origin.strip() for origin in self.cors_origins.split(",")]
        return self.cors_origins
    
settings = Settings()