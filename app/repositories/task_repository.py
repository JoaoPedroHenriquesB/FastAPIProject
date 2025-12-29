from typing import Annotated

from fastapi import Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from app.database.db_config import get_session
from app.models.task_model import TaskModel
from app.models.user_model import UserModel
from app.utils.token import get_current_user

T_CurrentUser = Annotated[UserModel, Depends(get_current_user)]
T_Session = Annotated[AsyncSession, Depends(get_session)]


class TaskRepository:
    def __init__(self, session: T_Session) -> None:
        self.session = session

    async def get_task_by_id(self, task_id):
        return await self.session.scalar(
            select(TaskModel).where(TaskModel.id == task_id)
        )

    async def verify_user(self, user_id):
        return select(TaskModel).where(TaskModel.user_id == user_id)

    # create a new task
    async def create_task(self, task_model: TaskModel):

        try:
            self.session.add(task_model)
            await self.session.commit()
            await self.session.refresh(task_model)
            return task_model

        except SQLAlchemyError as e:
            await self.session.rollback()
            raise e


    # get all tasks
    async def list_tasks(self, limit: int, offset: int):

        tasks = await self.session.scalars(select(TaskModel).limit(limit).offset(offset))
        return tasks.all()

    # get all tasks from user id
    async def get_tasks_from_user(self, user_id: int, task_filter, limit: int, offset: int):
        query = select(TaskModel).where(TaskModel.user_id == user_id)

        if task_filter.title:
            query = query.filter(TaskModel.title.contains(task_filter.title))

        if task_filter.description:
            query = query.filter(TaskModel.description.contains(task_filter.description))

        if task_filter.state:
            query = query.filter(TaskModel.state.contains(task_filter.state))

        result = await self.session.scalars(query.offset(offset).limit(limit))
        return result.all()

    # updates a task from an user
    async def update_user_task(self, task_model: TaskModel):

        try:
            self.session.add(task_model)
            await self.session.commit()
            await self.session.refresh(task_model)
            return task_model

        except SQLAlchemyError as e:
            await self.session.rollback()
            raise e

    async def delete_task(self, task_id):
        try:
            delete_task = await self.session.get(TaskModel, task_id)
            await self.session.delete(delete_task)
            await self.session.commit()

        except SQLAlchemyError as e:
            await self.session.rollback()
            raise e
