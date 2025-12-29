from enum import Enum

from app.database.db_config import Base
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column


class TaskState(str, Enum):
    draft = "draft"
    todo = "todo"
    doing = "doing"
    done = "done"
    trash = "trash"


class TaskModel(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    title: Mapped[str]
    description: Mapped[str]
    state: Mapped[TaskState]

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

