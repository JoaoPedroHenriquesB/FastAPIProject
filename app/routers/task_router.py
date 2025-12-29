from typing import Annotated

from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.db_config import get_session
from app.models.user_model import UserModel
from app.schemas.task_schema import TaskList, TaskPublic, TaskSchema, TaskUpdateSchema
from app.services.task_service import TaskService
from app.utils.misc import FilterTasks
from app.utils.token import get_current_user, requires_admin
from app.utils.task_exceptions import TaskNotFoundError

task_router = APIRouter(prefix="/tasks", tags=["tasks"])

T_Session = Annotated[AsyncSession, Depends(get_session)]


def task_service(session: T_Session) -> TaskService:
    return TaskService(session)


T_CurrentUser = Annotated[UserModel, Depends(get_current_user)]
T_Service = Annotated[TaskService, Depends(task_service)]
T_FilterTask = Annotated[FilterTasks, Query()]
T_Admin = Annotated[UserModel, Depends(requires_admin)]


# create task
@task_router.post("/create", response_model=TaskPublic, status_code=status.HTTP_201_CREATED)
async def create_task(task_schema: TaskSchema, current_user: T_CurrentUser, service: T_Service):

    user_id = current_user.id
    return await service.create_task(task_schema, user_id)


# get tasks
@task_router.get("/read", response_model=TaskList)
async def get_all_tasks(service: T_Service, filter_task: T_FilterTask, admin: T_Admin):

    all_tasks = await service.list_tasks(filter_task.limit, filter_task.offset)
    return {"tasks": all_tasks}


# get tasks from current user
@task_router.get("/my_tasks", response_model=TaskList)
async def tasks_from_user(service: T_Service,current_user: T_CurrentUser,task_filter: T_FilterTask,):
    try:
        tasks = await service.get_tasks_from_user(current_user, task_filter)
        return {"tasks": tasks}

    except TaskNotFoundError:
        raise HTTPException(status_code=404, detail="task not found")

# update user task
@task_router.patch("/update/{task_id}", response_model=TaskPublic)
async def update_task(service: T_Service, task_schema: TaskUpdateSchema, task_id: int, current_user: T_CurrentUser,):

    patch_task = await service.update_user_task(task_schema, task_id, current_user)
    return patch_task


# delete an task
@task_router.delete("/delete")
async def delete_task(service: T_Service, current_user: T_CurrentUser, task_id: int):

    await service.delete_task(task_id, current_user)
    return {"message": "task deleted successfully"}
