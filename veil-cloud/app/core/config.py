from __future__ import annotations

from functools import cached_property

from pydantic import EmailStr, Field, SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="VEIL_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Server Runtime
    environment: str = "development"
    host: str = "127.0.0.1"
    port: int = Field(default=8089, gt=0, le=65535)
    debug: bool = False

    # Persistent Storage (PostgreSQL)
    database_url: str = "postgresql+psycopg://veil:veil@localhost:5432/veil"

    # Cache & Ephemeral State (Redis)
    redis_url: str = Field(default="redis://localhost:6379/0", min_length=1)

    # Core Security & Access
    jwt_secret: SecretStr = Field(min_length=32)
    access_token_minutes: int = Field(default=30, gt=0, le=1440)
    password_reset_token_minutes: int = Field(default=30, gt=0, le=1440)
    password_reset_email_request_limit: int = Field(default=5, gt=0, le=50)
    password_reset_host_request_limit: int = Field(default=50, gt=0, le=1000)
    password_reset_request_window_seconds: int = Field(
        default=3600,
        gt=0,
        le=86400,
    )

    # Desktop & Frontend Ingress (CORS)
    cors_origins: str = (
        "http://127.0.0.1:5176,http://localhost:5176,"
        "tauri://localhost,http://tauri.localhost"
    )

    # Notification & Mail (SMTP)
    smtp_host: str | None = None
    smtp_port: int = Field(default=465, gt=0, le=65535)
    smtp_username: str | None = None
    smtp_password: SecretStr | None = None
    smtp_from_email: EmailStr | None = None
    smtp_from_name: str = "Veil by HackSmiths"
    smtp_starttls: bool = False
    smtp_ssl_tls: bool = True
    smtp_timeout_seconds: float = Field(default=10.0, gt=0, le=60)

    # Feedback & Admin Ingestion
    feedback_notification_email: EmailStr | None = None

    @field_validator("jwt_secret")
    @classmethod
    def reject_insecure_secret(cls, value: SecretStr) -> SecretStr:
        raw = value.get_secret_value()
        if raw.startswith("replace-this-") or raw.startswith("your_secret_key"):
            raise ValueError("Replace default VEIL_JWT_SECRET before starting Veil Cloud.")
        return value

    @model_validator(mode="after")
    def validate_smtp_configuration(self) -> Settings:
        smtp_configured = any((self.smtp_username, self.smtp_password, self.smtp_from_email))
        if smtp_configured and not self.smtp_host:
            raise ValueError("VEIL_SMTP_HOST is required when SMTP credentials are provided.")
        if bool(self.smtp_username) != bool(self.smtp_password):
            raise ValueError("Both VEIL_SMTP_USERNAME and VEIL_SMTP_PASSWORD must be configured.")
        if self.smtp_starttls and self.smtp_ssl_tls:
            raise ValueError("Enable only one of VEIL_SMTP_STARTTLS or VEIL_SMTP_SSL_TLS.")
        if self.smtp_host and not self.smtp_from_email:
            raise ValueError("VEIL_SMTP_FROM_EMAIL is required when VEIL_SMTP_HOST is set.")
        if self.feedback_notification_email and not self.smtp_host:
            raise ValueError("VEIL_FEEDBACK_NOTIFICATION_EMAIL requires VEIL_SMTP_HOST to be set.")
        return self

    @cached_property
    def allowed_origins(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.cors_origins.split(",")
            if origin.strip()
        ]

    @cached_property
    def email_enabled(self) -> bool:
        return bool(self.smtp_host and self.smtp_from_email)


settings = Settings()