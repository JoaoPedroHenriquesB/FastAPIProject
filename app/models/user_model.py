from datetime import datetime

from sqlalchemy import String, func, text
from sqlalchemy.orm import Mapped, mapped_column, registry

# it records the items that will be mapped in the database
table_registry = registry()


@table_registry.mapped_as_dataclass
class UserModel:
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    name: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    phone_number: Mapped[str | None] = mapped_column(String, nullable=True, unique=True)
    created_at: Mapped[datetime] = mapped_column(init=False, server_default=func.now())
    is_admin: Mapped[bool] = mapped_column(default=False, init=True, server_default=text("0"))
