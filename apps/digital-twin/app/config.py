"""Application configuration management."""

import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Databricks Configuration
    catalog: str = os.getenv("CATALOG", "caspers")
    simulator_schema: str = os.getenv("SIMULATOR_SCHEMA", "simulator")
    lakeflow_schema: str = os.getenv("LAKEFLOW_SCHEMA", "lakeflow")
    
    # Databricks SQL Connection
    databricks_host: Optional[str] = os.getenv("DATABRICKS_HOST")
    databricks_http_path: Optional[str] = os.getenv("DATABRICKS_HTTP_PATH")
    databricks_token: Optional[str] = os.getenv("DATABRICKS_TOKEN")
    
    # Application Configuration
    app_name: str = "caspers-digital-twin"
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    
    # CORS Settings
    cors_origins: list[str] = ["*"]  # Restrict in production
    
    # API Configuration
    api_v1_prefix: str = "/api/v1"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
