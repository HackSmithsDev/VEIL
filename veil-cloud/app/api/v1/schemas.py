from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class UserCreate(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=1, max_length=120)
    password: str = Field(min_length=12, max_length=128)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.lower()

    @field_validator("full_name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Name must not be empty")
        return value


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.lower()


class PasswordResetRequest(BaseModel):
    email: EmailStr

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.lower()


class PasswordResetConfirm(BaseModel):
    email: EmailStr
    reset_token: str = Field(min_length=32, max_length=128)
    new_password: str = Field(min_length=12, max_length=128)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.lower()


class MessageRead(BaseModel):
    message: str


class UserProfileUpdate(BaseModel):
    full_name: str = Field(min_length=1, max_length=120)

    @field_validator("full_name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Name must not be empty")
        return value


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    full_name: str
    created_at: datetime


class TokenRead(BaseModel):
    access_token: str
    token_type: Literal["bearer"] = "bearer"
    expires_in: int
    user: UserRead


class ProgramFields(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    version: str = Field(min_length=1, max_length=60)
    platform: str = Field(min_length=1, max_length=80)
    purpose: str | None = Field(default=None, max_length=1000)

    @field_validator("name", "version", "platform")
    @classmethod
    def validate_required_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("This field must not be empty")
        return value

    @field_validator("purpose")
    @classmethod
    def normalize_purpose(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        return value or None


class ProgramCreate(ProgramFields):
    pass


class ProgramUpdate(ProgramFields):
    pass


class ProgramRead(ProgramFields):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class FeedbackCreate(BaseModel):
    category: Literal["idea", "issue", "experience", "other"]
    message: str = Field(min_length=10, max_length=2000)

    @field_validator("message")
    @classmethod
    def validate_message(cls, value: str) -> str:
        value = value.strip()
        if len(value) < 10:
            raise ValueError("Feedback must be at least 10 characters")
        return value


class FeedbackRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    category: str
    message: str
    created_at: datetime
