"""
Token Golf - Configuration Management

Centralized settings using Pydantic Settings.
All configuration loaded from environment variables (.env file).
"""

from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    All settings can be overridden via environment variables.
    Default values are provided for development convenience.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # Ignore extra env vars not defined here
    )

    # ========================================================================
    # Application Environment
    # ========================================================================
    env: Literal["development", "production", "test"] = Field(
        default="development",
        description="Application environment"
    )

    log_level: Literal["debug", "info", "warning", "error", "critical"] = Field(
        default="info",
        description="Logging level"
    )

    log_format: Literal["json", "text"] = Field(
        default="text",
        description="Log output format"
    )

    debug: bool = Field(
        default=False,
        description="Enable debug mode (verbose logging, detailed errors)"
    )

    enable_docs: bool = Field(
        default=True,
        description="Enable FastAPI auto-generated docs at /docs"
    )

    # ========================================================================
    # Database Configuration
    # ========================================================================
    database_url: str = Field(
        default="sqlite+aiosqlite:///./data/token_golf.db",
        description="Database connection URL (SQLite or PostgreSQL)"
    )

    # PostgreSQL specific (only used when DATABASE_URL points to postgres)
    postgres_db: str | None = Field(
        default=None,
        description="PostgreSQL database name"
    )

    postgres_user: str | None = Field(
        default=None,
        description="PostgreSQL username"
    )

    postgres_password: str | None = Field(
        default=None,
        description="PostgreSQL password"
    )

    # ========================================================================
    # LLM Provider Configuration
    # ========================================================================
    claude_api_key: str = Field(
        default="",
        description="Claude API key from Anthropic console"
    )

    claude_model: str = Field(
        default="claude-haiku-4.5-20251001",
        description="Claude model to use (Haiku only for MVP)"
    )

    # OpenShift AI (not used in MVP, future)
    openshift_ai_url: str | None = Field(
        default=None,
        description="OpenShift AI endpoint URL"
    )

    openshift_ai_token: str | None = Field(
        default=None,
        description="OpenShift AI authentication token"
    )

    # ========================================================================
    # Game Configuration
    # ========================================================================
    session_timeout_hours: int = Field(
        default=3,
        ge=1,
        le=24,
        description="Session timeout in hours (default: 3)"
    )

    max_iterations_per_challenge: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Optional limit on attempts per challenge"
    )

    preload_challenges: bool = Field(
        default=True,
        description="Preload challenges on startup"
    )

    # ========================================================================
    # Security & Sessions
    # ========================================================================
    secret_key: str = Field(
        default="dev-secret-key-change-in-production",
        description="Secret key for session encryption (must change in production!)"
    )

    cors_origins: str = Field(
        default="http://localhost:8000,http://localhost:3000",
        description="Comma-separated list of allowed CORS origins"
    )

    # ========================================================================
    # Monitoring & Logging
    # ========================================================================
    sentry_dsn: str | None = Field(
        default=None,
        description="Sentry DSN for error tracking (optional)"
    )

    # ========================================================================
    # Validators
    # ========================================================================
    @field_validator("claude_api_key")
    @classmethod
    def validate_claude_api_key(cls, v: str, info) -> str:
        """Warn if Claude API key is not set (except in test environment)"""
        if info.data.get("env") != "test" and not v:
            import warnings
            warnings.warn(
                "CLAUDE_API_KEY not set. LLM features will not work. "
                "Get your key from: https://console.anthropic.com/"
            )
        return v

    @field_validator("secret_key")
    @classmethod
    def validate_secret_key(cls, v: str, info) -> str:
        """Error if using default secret key in production"""
        if info.data.get("env") == "production" and v == "dev-secret-key-change-in-production":
            raise ValueError(
                "SECRET_KEY must be changed in production! "
                "Generate one with: openssl rand -hex 32"
            )
        return v

    # ========================================================================
    # Helper Properties
    # ========================================================================
    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS origins string into list"""
        return [origin.strip() for origin in self.cors_origins.split(",")]

    @property
    def is_development(self) -> bool:
        """Check if running in development mode"""
        return self.env == "development"

    @property
    def is_production(self) -> bool:
        """Check if running in production mode"""
        return self.env == "production"

    @property
    def is_test(self) -> bool:
        """Check if running in test mode"""
        return self.env == "test"

    @property
    def using_sqlite(self) -> bool:
        """Check if using SQLite database"""
        return self.database_url.startswith("sqlite")

    @property
    def using_postgres(self) -> bool:
        """Check if using PostgreSQL database"""
        return self.database_url.startswith("postgresql")


@lru_cache
def get_settings() -> Settings:
    """
    Get cached settings instance.

    Uses lru_cache to ensure settings are loaded only once.
    This is the recommended pattern for FastAPI dependencies.

    Returns:
        Settings: Application settings

    Example:
        from app.config import get_settings

        settings = get_settings()
        print(settings.database_url)
    """
    return Settings()


# Convenience: Pre-instantiated settings for direct import
settings = get_settings()


# ============================================================================
# Usage Examples
# ============================================================================
if __name__ == "__main__":
    # This runs when you execute: python -m app.config
    import json

    settings = get_settings()

    print("Token Golf Configuration")
    print("=" * 60)
    print(f"Environment: {settings.env}")
    print(f"Debug Mode: {settings.debug}")
    print(f"Database: {settings.database_url}")
    print(f"Database Type: {'SQLite' if settings.using_sqlite else 'PostgreSQL'}")
    print(f"Claude Model: {settings.claude_model}")
    print(f"Session Timeout: {settings.session_timeout_hours}h")
    print(f"API Docs Enabled: {settings.enable_docs}")
    print(f"CORS Origins: {settings.cors_origins_list}")
    print("=" * 60)

    # Show all settings as JSON (excluding sensitive data)
    settings_dict = settings.model_dump()

    # Mask sensitive values
    sensitive_keys = ["claude_api_key", "secret_key", "postgres_password", "openshift_ai_token"]
    for key in sensitive_keys:
        if key in settings_dict and settings_dict[key]:
            settings_dict[key] = "***REDACTED***"

    print("\nFull Configuration:")
    print(json.dumps(settings_dict, indent=2))
