from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.v1.schemas import UserCreate, UserProfileUpdate
from app.core.exceptions import AccountAlreadyExistsError
from app.core.security import hash_password, verify_password
from app.db.models.user import User


def register_account(database: Session, payload: UserCreate) -> User:
    user = User(
        email=payload.email,
        full_name=payload.full_name,
        password_hash=hash_password(payload.password),
    )
    database.add(user)
    try:
        database.commit()
    except IntegrityError as error:
        database.rollback()
        raise AccountAlreadyExistsError from error
    database.refresh(user)
    return user


def authenticate_account(database: Session, email: str, password: str) -> User | None:
    user = database.scalar(select(User).where(User.email == email))
    if user is None or not verify_password(password, user.password_hash):
        return None
    return user


def update_account_profile(
    database: Session,
    user: User,
    payload: UserProfileUpdate,
) -> User:
    user.full_name = payload.full_name
    database.commit()
    database.refresh(user)
    return user
