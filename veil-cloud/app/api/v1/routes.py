import hashlib
import secrets
from hmac import compare_digest

from fastapi import APIRouter, BackgroundTasks, HTTPException, Request, Response, status
from redis.exceptions import RedisError
from sqlalchemy import select

from app.api.v1.dependencies import CurrentUser, DatabaseSession
from app.api.v1.schemas import (
    FeedbackCreate,
    FeedbackRead,
    MessageRead,
    PasswordResetConfirm,
    PasswordResetRequest,
    ProgramCreate,
    ProgramRead,
    ProgramUpdate,
    TokenRead,
    UserCreate,
    UserLogin,
    UserProfileUpdate,
    UserRead,
)
from app.core.config import settings
from app.core.exceptions import AccountAlreadyExistsError, ResourceNotFoundError
from app.core.security import create_access_token
from app.db.models.feedback import Feedback
from app.db.models.program import Program
from app.db.models.user import User
from app.services.accounts import (
    authenticate_account,
    register_account,
    reset_account_password,
    update_account_profile,
)
from app.services.feedback import list_user_feedback, submit_user_feedback
from app.services.email.sender import (
    send_feedback_emails,
    send_password_reset_email,
    send_welcome_email,
)
from app.services.programs import (
    create_user_program,
    delete_user_program,
    get_user_program,
    list_user_programs,
    update_user_program,
)
from app.utils.redis import (
    consume_password_reset_token,
    increment_rate_limit,
    set_password_reset_token,
)

router = APIRouter()
PASSWORD_RESET_MESSAGE = (
    "If an account exists for that email, password reset instructions will be sent."
)


@router.post("/auth/register", response_model=TokenRead, status_code=status.HTTP_201_CREATED)
def register_user(
    payload: UserCreate,
    background_tasks: BackgroundTasks,
    database: DatabaseSession,
) -> TokenRead:
    try:
        user = register_account(database, payload)
    except AccountAlreadyExistsError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists",
        ) from error
    access_token, expires_in = create_access_token(str(user.id))
    background_tasks.add_task(send_welcome_email, str(user.email), user.full_name)
    return TokenRead(access_token=access_token, expires_in=expires_in, user=user)


@router.post("/auth/login", response_model=TokenRead)
def login_user(payload: UserLogin, database: DatabaseSession) -> TokenRead:
    user = authenticate_account(database, payload.email, payload.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email or password is incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token, expires_in = create_access_token(str(user.id))
    return TokenRead(access_token=access_token, expires_in=expires_in, user=user)


@router.post(
    "/auth/password-reset/request",
    response_model=MessageRead,
    status_code=status.HTTP_202_ACCEPTED,
)
async def request_password_reset(
    payload: PasswordResetRequest,
    background_tasks: BackgroundTasks,
    request: Request,
    database: DatabaseSession,
) -> MessageRead:
    if not settings.email_enabled:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Password recovery is not configured on this service.",
        )

    email_digest = hashlib.sha256(payload.email.encode()).hexdigest()
    client_host = request.client.host if request.client else "unknown"
    host_digest = hashlib.sha256(client_host.encode()).hexdigest()
    try:
        attempts = await increment_rate_limit(
            f"password-reset:email:{email_digest}",
            settings.password_reset_request_window_seconds,
        )
        attempts_from_host = await increment_rate_limit(
            f"password-reset:host:{host_digest}",
            settings.password_reset_request_window_seconds,
        )
    except RedisError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Password recovery is temporarily unavailable.",
        ) from error

    if (
        attempts > settings.password_reset_email_request_limit
        or attempts_from_host > settings.password_reset_host_request_limit
    ):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many password reset requests. Try again later.",
        )

    reset_token = secrets.token_urlsafe(32)
    token_digest = hashlib.sha256(reset_token.encode()).hexdigest()
    expiration_seconds = settings.password_reset_token_minutes * 60
    try:
        await set_password_reset_token(
            token_digest,
            payload.email,
            expiration_seconds,
        )
    except RedisError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Password recovery is temporarily unavailable.",
        ) from error

    user = database.scalar(select(User).where(User.email == payload.email))
    if user is not None:
        background_tasks.add_task(
            send_password_reset_email,
            str(user.email),
            user.full_name,
            reset_token,
            settings.password_reset_token_minutes,
        )
    return MessageRead(message=PASSWORD_RESET_MESSAGE)


@router.post(
    "/auth/password-reset/confirm",
    response_model=MessageRead,
)
async def confirm_password_reset(
    payload: PasswordResetConfirm,
    database: DatabaseSession,
) -> MessageRead:
    token_digest = hashlib.sha256(payload.reset_token.encode()).hexdigest()
    try:
        token_email = await consume_password_reset_token(token_digest)
    except RedisError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Password recovery is temporarily unavailable.",
        ) from error

    if token_email is None or not compare_digest(token_email, payload.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This password reset code is invalid or expired.",
        )

    user = database.scalar(select(User).where(User.email == payload.email))
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This password reset code is invalid or expired.",
        )

    reset_account_password(database, user, payload.new_password)
    return MessageRead(message="Your password has been reset. You can now sign in.")


@router.get("/auth/me", response_model=UserRead)
def read_current_user(user: CurrentUser) -> User:
    return user


@router.get("/profile", response_model=UserRead)
def read_profile(user: CurrentUser) -> User:
    return user


@router.patch("/profile", response_model=UserRead)
def update_profile(
    payload: UserProfileUpdate,
    user: CurrentUser,
    database: DatabaseSession,
) -> User:
    return update_account_profile(database, user, payload)


@router.get("/programs", response_model=list[ProgramRead])
def list_programs(user: CurrentUser, database: DatabaseSession) -> list[Program]:
    return list_user_programs(database, user)


@router.post(
    "/programs",
    response_model=ProgramRead,
    status_code=status.HTTP_201_CREATED,
)
def create_program(
    payload: ProgramCreate,
    user: CurrentUser,
    database: DatabaseSession,
) -> Program:
    return create_user_program(database, user, payload)


@router.get("/programs/{program_id}", response_model=ProgramRead)
def read_program(
    program_id: int,
    user: CurrentUser,
    database: DatabaseSession,
) -> Program:
    try:
        return get_user_program(database, user, program_id)
    except ResourceNotFoundError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error


@router.put("/programs/{program_id}", response_model=ProgramRead)
def update_program(
    program_id: int,
    payload: ProgramUpdate,
    user: CurrentUser,
    database: DatabaseSession,
) -> Program:
    try:
        return update_user_program(database, user, program_id, payload)
    except ResourceNotFoundError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error


@router.delete("/programs/{program_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_program(
    program_id: int,
    user: CurrentUser,
    database: DatabaseSession,
) -> Response:
    try:
        delete_user_program(database, user, program_id)
    except ResourceNotFoundError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/feedback", response_model=list[FeedbackRead])
def list_feedback(user: CurrentUser, database: DatabaseSession) -> list[Feedback]:
    return list_user_feedback(database, user)


@router.post(
    "/feedback",
    response_model=FeedbackRead,
    status_code=status.HTTP_201_CREATED,
)
def submit_feedback(
    payload: FeedbackCreate,
    background_tasks: BackgroundTasks,
    user: CurrentUser,
    database: DatabaseSession,
) -> Feedback:
    feedback = submit_user_feedback(database, user, payload)
    background_tasks.add_task(
        send_feedback_emails,
        str(user.email),
        user.full_name,
        feedback.category,
        feedback.message,
    )
    return feedback


@router.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
