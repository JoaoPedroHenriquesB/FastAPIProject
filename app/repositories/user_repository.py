from fastapi import Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.db_config import get_session
from app.models.user_model import UserModel


class UserRepository:
    def __init__(self, session: AsyncSession = Depends(get_session)):
        self.session = session

    # verify if email or phone number already exists in database
    async def verify_data(self, email: str, phone_number: str):
        return await self.session.scalar(
            select(UserModel).where(
                (UserModel.email == email) | (UserModel.phone_number == phone_number)
            )
        )

    # create a new user
    async def new_user(self, user_model: UserModel):
        try:
            self.session.add(user_model)
            await self.session.commit()
            await self.session.refresh(user_model)
            return user_model
        except Exception as e:
            await self.session.rollback()
            print(f"ERROR: {e}")
            raise HTTPException(status_code=500, detail="Internal Error")

    # get all users from database
    async def get_all(self, limit: int, offset: int):
        try:
            result = await self.session.scalars(
                select(UserModel).limit(limit).offset(offset)
            )

            return result.all()

        except Exception as e:
            print(f"ERROR: {e}")
            raise HTTPException(status_code=500, detail="Internal Error")

    # get user from id
    async def get_user_id(self, user_id):
        return await self.session.scalar(
            select(UserModel).where(UserModel.id == user_id)
        )

    # update a user
    async def patch_user(self, user_model: UserModel):

        try:
            self.session.add(user_model)
            await self.session.commit()
            await self.session.refresh(user_model)
            return user_model

        except Exception as e:
            await self.session.rollback()
            print(f"ERROR: {e}")
            raise HTTPException(status_code=500, detail="Internal Error")

    # delete a user
    async def delete_user(self, user_id):
        try:
            user_to_delete = await self.session.get(UserModel, user_id)
            await self.session.delete(user_to_delete)
            await self.session.commit()

        except Exception as e:
            await self.session.rollback()
            print(f"ERROR: {e}")
            raise HTTPException(status_code=500, detail="Internal Error")
