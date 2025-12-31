from datetime import datetime

from sqlalchemy import String, func, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.db_config import Base
from app.models.task_model import TaskModel


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    name: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    phone_number: Mapped[str | None] = mapped_column(String, nullable=True, unique=True)
    created_at: Mapped[datetime] = mapped_column(init=False, server_default=func.now())
    is_admin: Mapped[bool] = mapped_column(
        default=False, init=True, server_default=text("false")
    )

    # 1:N, a user can have N tasks
    tasks: Mapped[list["TaskModel"]] = relationship(
        init=False, cascade="all, delete-orphan", lazy="selectin"
    )
