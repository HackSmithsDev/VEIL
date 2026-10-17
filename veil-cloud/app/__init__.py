import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import settings


def create_app() -> FastAPI:
    if settings.email_enabled:
        logging.getLogger(__name__).info("SMTP email delivery is configured")
    else:
        logging.getLogger(__name__).warning(
            "SMTP email delivery is disabled; configure VEIL_SMTP_* to enable it"
        )
    application = FastAPI(
        title="VEIL Cloud API",
        version="0.1.0",
        description="Account and metadata service for VEIL Guard.",
    )
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=False,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type"],
    )
    application.include_router(api_router)
    return application

app = create_app()