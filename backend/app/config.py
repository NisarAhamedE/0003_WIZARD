from pydantic_settings import BaseSettings
from typing import List
import os
from urllib.parse import quote_plus
from dotenv import load_dotenv

# Load .env from parent directory
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '..', '.env'))


class Settings(BaseSettings):
    # Database - using existing .env format
    DB_HOST: str = "127.0.0.1"
    DB_PORT: int = 5432
    DB_NAME: str = "wizarddb"
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "@dmin123"

    @property
    def DATABASE_URL(self) -> str:
        # URL-encode the password to handle special characters like @
        encoded_password = quote_plus(self.DB_PASSWORD)
        return f"postgresql://{self.DB_USER}:{encoded_password}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20

    # JWT Configuration
    SECRET_KEY: str = "your-super-secret-key-change-this-in-production-2024"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Application Settings
    APP_NAME: str = "Multi-Wizard Platform"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"

    # CORS Settings - set CORS_ORIGINS env var as comma-separated list
    # e.g., CORS_ORIGINS="http://localhost:3000,https://your-frontend.railway.app"
    CORS_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000,https://desirable-essence-production-6e00.up.railway.app"
    CORS_ALLOW_CREDENTIALS: bool = True

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS_ORIGINS string into a list."""
        if isinstance(self.CORS_ORIGINS, list):
            return self.CORS_ORIGINS
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    # File Upload Settings
    MAX_UPLOAD_SIZE: int = 10485760  # 10MB
    UPLOAD_DIR: str = "./uploads"
    ALLOWED_EXTENSIONS: List[str] = ["jpg", "jpeg", "png", "pdf", "doc", "docx"]

    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_PERIOD: int = 60  # seconds

    class Config:
        env_file = "../../.env"
        case_sensitive = True
        extra = "allow"


settings = Settings()
