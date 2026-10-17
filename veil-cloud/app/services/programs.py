from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.v1.schemas import ProgramCreate, ProgramUpdate
from app.core.exceptions import ResourceNotFoundError
from app.db.models.program import Program
from app.db.models.user import User


def list_user_programs(database: Session, user: User) -> list[Program]:
    return list(
        database.scalars(
            select(Program)
            .where(Program.owner_id == user.id)
            .order_by(Program.updated_at.desc(), Program.id.desc())
        )
    )


def create_user_program(
    database: Session,
    user: User,
    payload: ProgramCreate,
) -> Program:
    program = Program(owner_id=user.id, **payload.model_dump())
    database.add(program)
    database.commit()
    database.refresh(program)
    return program


def get_user_program(database: Session, user: User, program_id: int) -> Program:
    program = database.scalar(
        select(Program).where(Program.id == program_id, Program.owner_id == user.id)
    )
    if program is None:
        raise ResourceNotFoundError("Program not found")
    return program


def update_user_program(
    database: Session,
    user: User,
    program_id: int,
    payload: ProgramUpdate,
) -> Program:
    program = get_user_program(database, user, program_id)
    for field, value in payload.model_dump().items():
        setattr(program, field, value)
    database.commit()
    database.refresh(program)
    return program


def delete_user_program(database: Session, user: User, program_id: int) -> None:
    program = get_user_program(database, user, program_id)
    database.delete(program)
    database.commit()
