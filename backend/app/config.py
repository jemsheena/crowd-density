"""Application configuration from environment variables."""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    DEBUG: bool = False

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_STREAM_PREFIX: str = "stream"

    # S3/MinIO
    S3_ENDPOINT_URL: str = "http://localhost:9000"
    S3_ACCESS_KEY: str = "minioadmin"
    S3_SECRET_KEY: str = "minioadmin"
    S3_BUCKET: str = "crowd-density"
    S3_REGION: str = "us-east-1"
    S3_USE_SSL: bool = False

    # Models
    MODEL_DIR: str = "./models"
    YOLO_MODEL_PATH: str = "yolov8n"
    CSRNET_MODEL_PATH: str = "csrnet_v1.pt"

    # Auth
    JWT_SECRET_KEY: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    AUTH_DISABLED: bool = True  # For dev

    # Inference
    DEFAULT_INFERENCE_MODE: str = "hybrid"  # "detector" | "density" | "hybrid"
    HYBRID_THRESHOLD_LOW: float = 120.0
    HYBRID_THRESHOLD_HIGH: float = 180.0
    DEFAULT_EMA_ALPHA: float = 0.7

    # Rate limiting
    RATE_LIMIT_PER_SECOND: int = 20

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

