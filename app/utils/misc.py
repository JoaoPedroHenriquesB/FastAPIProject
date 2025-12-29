from pydantic import BaseModel, Field

from app.models.task_model import TaskState


class FilterPage(BaseModel):
    offset: int = Field(ge=0, default=0)
    limit: int = Field(ge=1, default=100)


class FilterTasks(FilterPage):
    title: str | None = Field(default=None, min_length=3, max_length=50)
    description: str | None = Field(default=None, min_length=3)
    state: TaskState | None = Field(default=None)
