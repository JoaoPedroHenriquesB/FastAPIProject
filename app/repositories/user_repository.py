from fastapi import Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.db_config import get_session
from app.models.user_model import UserModel


class UserRepository:
    def __init__(self, session: Session = Depends(get_session)):
        self.session = session

    # verify if email or phone number already exists in database
    def verify_data(self, email: str, phone_number: str):
        return self.session.scalar(
            select(UserModel).where(
                (UserModel.email == email) | (UserModel.phone_number == phone_number)
            )
        )

    # create a new user
    def new_user(self, user_model: UserModel):
        try:
            self.session.add(user_model)
            self.session.commit()
            self.session.refresh(user_model)
            return user_model
        except Exception as e:
            self.session.rollback()
            print(f"ERROR: {e}")
            raise HTTPException(status_code=500, detail="Internal Error")

    # get all users from database
    def get_all(self, limit: int, offset: int):
        try:
            return self.session.scalars(
                select(UserModel).limit(limit).offset(offset)
            ).all()
        except Exception as e:
            print(f"ERROR: {e}")
            raise HTTPException(status_code=500, detail="Internal Error")

    # get user from id
    def get_user_id(self, user_id):
        return self.session.scalar(select(UserModel).where(UserModel.id == user_id))

    # update a user
    def patch_user(self, user_model: UserModel):

        try:
            self.session.add(user_model)
            self.session.commit()
            self.session.refresh(user_model)
            return user_model

        except Exception as e:
            self.session.rollback()
            print(f"ERROR: {e}")
            raise HTTPException(status_code=500, detail="Internal Error")

    def delete_user(self, user_id):
        try:
            self.session.delete(user_id)
            self.session.commit()
            return {"message": f"User deleted from database"}

        except Exception as e:
            self.session.rollback()
            print(f"ERROR: {e}")
            raise HTTPException(status_code=500, detail="Internal Error")
