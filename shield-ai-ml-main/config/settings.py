"""
SHIELD AI - Application Settings
Centralized configuration management
"""

import os
from typing import List, Optional
from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    Uses pydantic-settings for automatic env loading.
    """
    
    # Environment
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")
    DEBUG: bool = Field(default=True, env="DEBUG")
    
    # API Configuration
    API_HOST: str = Field(default="0.0.0.0", env="API_HOST")
    API_PORT: int = Field(default=8000, env="API_PORT")
    API_PREFIX: str = Field(default="/api/v1", env="API_PREFIX")
    API_TITLE: str = Field(default="SHIELD AI Safety API", env="API_TITLE")
    API_VERSION: str = Field(default="2.0.0", env="API_VERSION")
    
    # Security
    SECRET_KEY: str = Field(default="your-secret-key-change-in-production", env="SECRET_KEY")
    API_KEY_HEADER: str = Field(default="X-API-Key", env="API_KEY_HEADER")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # CORS
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8080", "*"],
        env="CORS_ORIGINS"
    )
    
    # Database (Supabase)
    SUPABASE_URL: Optional[str] = Field(default=None, env="SUPABASE_URL")
    SUPABASE_KEY: Optional[str] = Field(default=None, env="SUPABASE_KEY")
    SUPABASE_SERVICE_KEY: Optional[str] = Field(default=None, env="SUPABASE_SERVICE_KEY")
    
    # Redis (Optional caching)
    REDIS_URL: Optional[str] = Field(default=None, env="REDIS_URL")
    REDIS_PASSWORD: Optional[str] = Field(default=None, env="REDIS_PASSWORD")
    
    # ML Model Configuration
    MODEL_CACHE_DIR: str = Field(default="./models/cache", env="MODEL_CACHE_DIR")
    MODEL_TYPE: str = Field(default="gradient_boosting", env="MODEL_TYPE")
    MODEL_AUTO_RETRAIN: bool = Field(default=False, env="MODEL_AUTO_RETRAIN")
    
    # External APIs
    GOOGLE_MAPS_API_KEY: Optional[str] = Field(default=None, env="GOOGLE_MAPS_API_KEY")
    MAPBOX_ACCESS_TOKEN: Optional[str] = Field(default=None, env="MAPBOX_ACCESS_TOKEN")
    CRIME_API_URL: Optional[str] = Field(default=None, env="CRIME_API_URL")
    CRIME_API_KEY: Optional[str] = Field(default=None, env="CRIME_API_KEY")
    
    # Feature Flags
    ENABLE_STALKING_DETECTION: bool = Field(default=True, env="ENABLE_STALKING_DETECTION")
    ENABLE_ROUTE_ANOMALY: bool = Field(default=True, env="ENABLE_ROUTE_ANOMALY")
    ENABLE_EMERGENCY_PROTOCOL: bool = Field(default=True, env="ENABLE_EMERGENCY_PROTOCOL")
    ENABLE_ML_PREDICTIONS: bool = Field(default=True, env="ENABLE_ML_PREDICTIONS")
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = Field(default=True, env="RATE_LIMIT_ENABLED")
    RATE_LIMIT_DEFAULT_RPM: int = Field(default=60, env="RATE_LIMIT_DEFAULT_RPM")
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_FILE: Optional[str] = Field(default=None, env="LOG_FILE")
    LOG_FORMAT: str = Field(default="json", env="LOG_FORMAT")
    
    # Privacy Settings
    RAW_GPS_RETENTION_SECONDS: int = Field(default=0, env="RAW_GPS_RETENTION_SECONDS")
    PATTERN_RETENTION_DAYS: int = Field(default=90, env="PATTERN_RETENTION_DAYS")
    GPS_PRECISION_DECIMALS: int = Field(default=4, env="GPS_PRECISION_DECIMALS")
    
    # Performance
    MAX_RISK_CALC_MS: int = Field(default=200, env="MAX_RISK_CALC_MS")
    MAX_INFERENCE_MS: int = Field(default=100, env="MAX_INFERENCE_MS")
    CACHE_TTL_SECONDS: int = Field(default=60, env="CACHE_TTL_SECONDS")
    
    # Notification Services
    NOTIFICATION_WEBHOOK_URL: Optional[str] = Field(default=None, env="NOTIFICATION_WEBHOOK_URL")
    EMERGENCY_WEBHOOK_URL: Optional[str] = Field(default=None, env="EMERGENCY_WEBHOOK_URL")
    
    # Monitoring
    SENTRY_DSN: Optional[str] = Field(default=None, env="SENTRY_DSN")
    PROMETHEUS_ENABLED: bool = Field(default=False, env="PROMETHEUS_ENABLED")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Create model cache directory if it doesn't exist
        Path(self.MODEL_CACHE_DIR).mkdir(parents=True, exist_ok=True)
    
    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT.lower() == "production"
    
    @property
    def is_development(self) -> bool:
        return self.ENVIRONMENT.lower() == "development"
    
    @property
    def database_configured(self) -> bool:
        return bool(self.SUPABASE_URL and self.SUPABASE_KEY)
    
    @property
    def cache_configured(self) -> bool:
        return bool(self.REDIS_URL)


# Create singleton settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get the application settings instance"""
    return settings


def reload_settings() -> Settings:
    """Reload settings from environment"""
    global settings
    settings = Settings()
    return settings
