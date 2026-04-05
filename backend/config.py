from pydantic_settings import BaseSettings
from typing import List, Optional
import json

class Settings(BaseSettings):
    # Application
    app_name: str = "Task Manager"
    app_version: str = "1.0.0"
    debug: bool = True
    secret_key: str = "change-me-in-production"
    
    # Database
    database_url: str = "sqlite:///./data/tasks.db"
    
    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_prefix: str = "/api/v1"
    
    # CORS
    cors_origins: List[str] = ["http://localhost:8501", "http://localhost:8000"]
    
    # Email
    smtp_enabled: bool = False
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: Optional[str] = None
    smtp_password: Optional[str] = None
    smtp_from_email: str = "noreply@taskmanager.com"
    
    # Notifications
    notification_hours_before: int = 24
    notification_check_interval: int = 3600
    
    # Logging
    log_level: str = "INFO"
    log_file: str = "./logs/app.log"
    
    # Security
    bcrypt_rounds: int = 12
    jwt_expiration_minutes: int = 30
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        
        @classmethod
        def parse_env_var(cls, field_name: str, raw_val: str):
            if field_name == "cors_origins":
                return json.loads(raw_val)
            return raw_val

settings = Settings()