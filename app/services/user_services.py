from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user_model import UserModel
from app.repositories.user_repository import UserRepository
from app.utils.hash_password import hash_password


class UserService:
    def __init__(self, session: AsyncSession):
        self.repository = UserRepository(session)

    async def create_user(self, user_data):
        existing_user = await self.repository.verify_data(
            user_data.email, user_data.phone_number
        )

        if existing_user:
            if existing_user.email == user_data.email:
                raise ValueError(400, "Email already exists")

            if existing_user.phone_number == user_data.phone_number:
                raise ValueError(400, "Phone Number already exists")

        new_user = UserModel(
            name=user_data.name,
            email=user_data.email,
            password=hash_password(user_data.password),
            phone_number=user_data.phone_number,
            is_admin=user_data.is_admin,
        )

        try:
            return await self.repository.new_user(new_user)
        except Exception as e:
            print(f"ERROR: {e}")
            raise HTTPException(500, detail="Internal Error")

    async def find_by_id(self, user_id: int):
        user = await self.repository.get_user_id(user_id)

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if user is None:
            raise ValueError("User not exists")

        return user

    async def list_users(self, limit: int, offset: int):
        users = await self.repository.get_all(limit, offset)

        try:
            if not users:
                HTTPException(status_code=404, detail="No users Found")

            return users

        except ValueError as e:
            print(f"ERROR: {e}")
            raise HTTPException(500, detail="Internal Error")

    async def update_user(self, user_data, user_id: int):
        db_user = await self.repository.get_user_id(user_id)

        if not db_user:
            raise ValueError("User not found")

        db_user.name = user_data.name
        db_user.email = user_data.email
        db_user.password = hash_password(user_data.password)
        db_user.phone_number = user_data.phone_number

        try:
            return await self.repository.patch_user(db_user)

        except Exception as e:
            print(f"ERROR: {e}")
            raise HTTPException(500, detail="Internal Error")

    async def user_delete(self, user_id):
        db_user = await self.repository.get_user_id(user_id)

        if not db_user:
            raise HTTPException(status_code=400, detail="User not found")

        try:
            return await self.repository.delete_user(user_id)

        except Exception as e:
            print(f"ERROR: {e}")
            raise HTTPException(500, detail="Internal Error")
