from pydantic_settings import BaseSettings
from typing import List
import os
from urllib.parse import quote_plus
from dotenv import load_dotenv

# Load .env from parent directory (override=True to ensure .env values take precedence)
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '..', '.env'), override=True)


class Settings(BaseSettings):
    # Database - Railway provides DATABASE_URL, local dev uses individual vars
    DATABASE_URL: str = ""  # Railway sets this automatically

    # Local development fallback
    DB_HOST: str = "127.0.0.1"
    DB_PORT: int = 5432
    DB_NAME: str = "wizarddb"
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "@dmin123"

    @property
    def database_url(self) -> str:
        """Get database URL - use DATABASE_URL if set (Fly.io/Railway), otherwise build from parts."""
        if self.DATABASE_URL:
            # Fly.io/Heroku use postgres:// but SQLAlchemy requires postgresql://
            url = self.DATABASE_URL
            if url.startswith("postgres://"):
                url = url.replace("postgres://", "postgresql://", 1)
            return url
        # Fallback for local development
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
    # e.g., CORS_ORIGINS="http://localhost:3000,https://your-frontend.fly.dev"
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:3001,http://127.0.0.1:3000,http://127.0.0.1:3001,https://0003-wizard-frontend.fly.dev,https://0003-wizard-dyttbg.fly.dev"
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
