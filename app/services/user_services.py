import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user_model import UserModel
from app.repositories.user_repository import UserRepository
from app.utils.exceptions import (
    DuplicateEntityError,
    InternalDomainError,
    NotFoundError,
    PermissionDeniedError,
)
from app.utils.hash_password import hash_password

logger = logging.getLogger(__name__)


class UserService:
    def __init__(self, session: AsyncSession):
        self.repository = UserRepository(session)

    async def create_user(self, user_data):
        existing_user = await self.repository.verify_data(
            user_data.email, user_data.phone_number
        )

        if existing_user:
            if existing_user.email == user_data.email:
                raise DuplicateEntityError("email", "email already exists")

            if existing_user.phone_number == user_data.phone_number:
                raise DuplicateEntityError(
                    "phone-number", "phone-number already exists"
                )

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
            logger.exception(f"internal server error occured: {e}")
            raise InternalDomainError()

    async def find_by_id(self, user_id: int):
        user = await self.repository.get_user_id(user_id)

        if not user:
            raise NotFoundError()

        if user is None:
            raise ValueError("User not exists")

        return user

    async def list_users(self, limit: int, offset: int):
        users = await self.repository.get_all(limit, offset)

        try:
            if not users:
                raise NotFoundError()

            return users

        except ValueError as e:
            logger.exception(e)
            raise InternalDomainError()

    async def update_user(self, user_data, user_id: int, current_user):
        db_user = await self.repository.get_user_id(user_id)

        if current_user.id != user_id:
            raise PermissionDeniedError()

        if not db_user:
            raise NotFoundError()

        db_user.name = user_data.name
        db_user.email = user_data.email
        db_user.password = hash_password(user_data.password)
        db_user.phone_number = user_data.phone_number

        try:
            return await self.repository.patch_user(db_user)

        except Exception as e:
            logger.exception(e)
            raise InternalDomainError()

    async def user_delete(self, user_id):
        db_user = await self.repository.get_user_id(user_id)

        if not db_user:
            raise NotFoundError()

        try:
            return await self.repository.delete_user(user_id)

        except Exception as e:
            logger.exception(e)
            raise InternalDomainError()
