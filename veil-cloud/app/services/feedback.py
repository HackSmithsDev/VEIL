from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.v1.schemas import FeedbackCreate
from app.db.models.feedback import Feedback
from app.db.models.user import User


def list_user_feedback(database: Session, user: User) -> list[Feedback]:
    return list(
        database.scalars(
            select(Feedback)
            .where(Feedback.owner_id == user.id)
            .order_by(Feedback.created_at.desc(), Feedback.id.desc())
        )
    )


def submit_user_feedback(
    database: Session,
    user: User,
    payload: FeedbackCreate,
) -> Feedback:
    feedback = Feedback(owner_id=user.id, **payload.model_dump())
    database.add(feedback)
    database.commit()
    database.refresh(feedback)
    return feedback
