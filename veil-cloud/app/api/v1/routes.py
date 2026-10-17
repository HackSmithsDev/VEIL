from fastapi import APIRouter, BackgroundTasks, HTTPException, Response, status

from app.api.v1.dependencies import CurrentUser, DatabaseSession
from app.api.v1.schemas import (
    FeedbackCreate,
    FeedbackRead,
    ProgramCreate,
    ProgramRead,
    ProgramUpdate,
    TokenRead,
    UserCreate,
    UserLogin,
    UserProfileUpdate,
    UserRead,
)
from app.core.exceptions import AccountAlreadyExistsError, ResourceNotFoundError
from app.core.security import create_access_token
from app.db.models.feedback import Feedback
from app.db.models.program import Program
from app.db.models.user import User
from app.services.accounts import (
    authenticate_account,
    register_account,
    update_account_profile,
)
from app.services.feedback import list_user_feedback, submit_user_feedback
from app.services.email.sender import send_feedback_emails, send_welcome_email
from app.services.programs import (
    create_user_program,
    delete_user_program,
    get_user_program,
    list_user_programs,
    update_user_program,
)

router = APIRouter()


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
