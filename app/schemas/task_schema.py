from pydantic import BaseModel, ConfigDict, Field

from app.models.task_model import TaskState


class TaskSchema(BaseModel):
    title: str
    description: str
    state: TaskState = Field(default=TaskState.todo)


class TaskPublic(TaskSchema):
    id: int

    model_config = ConfigDict(from_attributes=True)


class TaskList(BaseModel):
    tasks: list[TaskPublic]


class TaskUpdateSchema(BaseModel):
    title: str | None = None
    description: str | None = None
    state: TaskState | None = None
