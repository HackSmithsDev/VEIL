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

    environment: str = "development"
    database_url: str = "postgresql+psycopg://veil:veil@localhost:5432/veil"
    redis_url: str = Field(default="redis://localhost:6379/0", min_length=1)
    jwt_secret: SecretStr = Field(min_length=32)
    access_token_minutes: int = Field(default=30, gt=0, le=1440)
    cors_origins: str = (
        "http://127.0.0.1:5176,http://localhost:5176,"
        "tauri://localhost,http://tauri.localhost"
    )
    smtp_host: str | None = None
    smtp_port: int = Field(default=587, gt=0, le=65535)
    smtp_username: str | None = None
    smtp_password: SecretStr | None = None
    smtp_from_email: EmailStr | None = None
    smtp_from_name: str = "VEIL Guard"
    smtp_starttls: bool = True
    smtp_ssl_tls: bool = False
    smtp_timeout_seconds: float = Field(default=10, gt=0, le=60)
    feedback_notification_email: EmailStr | None = None

    @field_validator("jwt_secret")
    @classmethod
    def reject_example_secret(cls, value: SecretStr) -> SecretStr:
        if value.get_secret_value().startswith("replace-this-"):
            raise ValueError("Replace the example JWT secret before starting the service")
        return value

    @model_validator(mode="after")
    def validate_smtp_settings(self) -> "Settings":
        smtp_options_set = any(
            (
                self.smtp_username,
                self.smtp_password,
                self.smtp_from_email,
            )
        )
        if smtp_options_set and not self.smtp_host:
            raise ValueError("VEIL_SMTP_HOST is required when SMTP options are configured")
        if bool(self.smtp_username) != bool(self.smtp_password):
            raise ValueError("Configure both VEIL_SMTP_USERNAME and VEIL_SMTP_PASSWORD")
        if self.smtp_starttls and self.smtp_ssl_tls:
            raise ValueError("Enable only one of VEIL_SMTP_STARTTLS and VEIL_SMTP_SSL_TLS")
        if self.smtp_host and not self.smtp_from_email:
            raise ValueError("VEIL_SMTP_FROM_EMAIL is required when SMTP is configured")
        if self.feedback_notification_email and not self.smtp_host:
            raise ValueError(
                "VEIL_FEEDBACK_NOTIFICATION_EMAIL requires VEIL_SMTP_HOST to be configured"
            )
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