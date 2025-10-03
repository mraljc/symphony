from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Keycloak Configuration
    debug: bool = False #callelarm
    environment: str = "development" #callelarm
    keycloak_server_url: str = "http://keycloak:8080"
    keycloak_realm: str = "symphony"
    keycloak_client_id: str = "symphony-client"
    keycloak_client_secret: str = "change-me"
    keycloak_admin_user: str = "admin"
    keycloak_admin_password: str = "admin"

    # Database Configuration
    database_url: str = "postgresql+asyncpg://user:pass@postgres:5432/symphony_auth"

    # Redis Configuration
    redis_url: str = "redis://redis-cluster:6379"

    # Vault Configuration
    vault_url: str = "http://vault:8200"
    vault_token: str = "change-me"

    # Security Configuration
    token_expiry_minutes: int = 60
    refresh_token_expiry_days: int = 30

    class Config:
        env_file = ".env"

settings = Settings()