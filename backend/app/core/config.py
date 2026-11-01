from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    PROJECT_NAME: str = "NullSpace"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    DATABASE_URL: str = "sqlite:///./nullspace.db"
    
    # AI Provider configuration (optional)
    AI_PROVIDER: str = "local_fallback" # "local_fallback", "gemini", "openai"
    OPENAI_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    
    # Ingestion & SSRF Safety
    MAX_RESPONSE_SIZE_BYTES: int = 2 * 1024 * 1024  # 2MB
    HTTP_TIMEOUT_SECONDS: float = 10.0
    MAX_REDIRECTS: int = 3
    USER_AGENT: str = "NullSpace-Epistemic-Engine/1.0 (+https://nullspace.local)"
    
    # Temporal settings
    CURRENT_REFERENCE_YEAR: int = 2026
    STALE_YEAR_THRESHOLD: int = 1  # Older than current - 1 is potentially stale
    
    # Priority Scoring Weights
    WEIGHT_IMPORTANCE: float = 0.35
    WEIGHT_MISSING: float = 0.30
    WEIGHT_CONTRADICTION: float = 0.20
    WEIGHT_TEMPORAL: float = 0.15

settings = Settings()
