from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.task_model import TaskModel
from app.repositories.task_repository import TaskRepository
from app.utils.task_exceptions import TaskNotFoundError

class TaskService:
    def __init__(self, session: AsyncSession):
        self.repository = TaskRepository(session)

    # create a new task
    async def create_task(self, task_data, user_id: int):

        new_task = TaskModel(
            title=task_data.title,
            description=task_data.description,
            state=task_data.state,
            user_id=user_id,
        )

        try:
            return await self.repository.create_task(new_task)

        except Exception as e:
            print(f"ERROR: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error while creating task",
            )

    # get all tasks from all users
    async def list_tasks(self, limit: int, offset: int):
        tasks = await self.repository.list_tasks(limit, offset)

        if not tasks:
            raise TaskNotFoundError()

        return tasks


    # get all tasks from an user
    async def get_tasks_from_user(self, current_user, task_filter):

        users_task = await self.repository.get_tasks_from_user(
            user_id=current_user.id,
            task_filter=task_filter,
            limit=task_filter.limit,
            offset=task_filter.offset,
        )

        if not users_task:
            raise TaskNotFoundError()

        return users_task

    # update a task
    async def update_user_task(self, task_data, task_id: int, current_user):
        updated_task = await self.repository.get_task_by_id(task_id)

        if not updated_task:
            raise HTTPException(status_code=404, detail="No task found")

        if current_user.id != updated_task.user_id:
            raise HTTPException(status_code=401, detail="Unauthorized")

        update_data = task_data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(updated_task, field, value)

        try:
            return await self.repository.update_user_task(updated_task)

        except ValueError as e:
            print(f"ERROR: {e}")
            raise HTTPException(500, detail="Internal Error while updating task")

    # delete task
    async def delete_task(self, task_id: int, current_user):
        db_task = await self.repository.get_task_by_id(task_id)

        if db_task is None:
            raise HTTPException(status_code=404, detail="No task found")

        if current_user.id != db_task.user_id:
            raise HTTPException(status_code=401, detail="Not Allowed")

        try:
            return await self.repository.delete_task(task_id)

        except Exception as e:
            print(f"ERROR: {e}")
            raise HTTPException(500, detail="Internal Error while deleting task")
