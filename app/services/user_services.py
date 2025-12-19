from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.user_model import UserModel
from app.repositories.user_repository import UserRepository
from app.utils.hash_password import hash_password


class UserService:
    def __init__(self, session: Session):
        self.repository = UserRepository(session)

    def create_user(self, user_data):
        existing_user = self.repository.verify_data(
            user_data.email, user_data.phone_number
        )

        if existing_user:
            if existing_user.email == UserModel.email:
                raise ValueError("Email already exists")

            if existing_user.phone_number == UserModel.phone_number:
                raise ValueError("Phone Number already exists")

        new_user = UserModel(
            name=user_data.name,
            email=user_data.email,
            password=hash_password(user_data.password),
            phone_number=user_data.phone_number,
        )

        try:
            return self.repository.new_user(new_user)
        except Exception as e:
            print(f"ERROR: {e}")
            raise HTTPException(500, detail="Internal Error")

    def find_by_id(self, user_id: int):
        user = self.repository.get_user_id(user_id)

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if user is None:
            raise ValueError("User not exists")

        return user

    def list_users(self, limit: int, offset: int):
        users = self.repository.get_all(limit, offset)
        try:
            return users if users is not None else []
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))

    def update_user(self, user_data, user_id: int):
        db_user = self.repository.get_user_id(user_id)

        if not db_user:
            raise ValueError("User not found")

        db_user.name = user_data.name
        db_user.email = user_data.email
        db_user.password = hash_password(user_data.password)
        db_user.phone_number = user_data.phone_number

        try:
            return self.repository.patch_user(db_user)

        except Exception as e:
            print(f"ERROR: {e}")
            raise HTTPException(500, detail="Internal Error")

    def user_delete(self, user_id):
        try:
            return self.repository.delete_user(user_id)

        except Exception as e:
            print(f"ERROR: {e}")
            raise HTTPException(500, detail="Internal Error")
