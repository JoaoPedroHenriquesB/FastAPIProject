from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database.db_config import get_session
from app.models.user_model import UserModel
from app.schemas.users_schema import UserCreateSchema, UserList, UserPublic
from app.utils.hash_password import hash_password

router = APIRouter(prefix="/users", tags=["users"])

database = []


# CREATE
@router.post("/create", status_code=201, response_model=UserPublic)
async def create_user(
    user: UserCreateSchema, session: Session = Depends(get_session)
) -> UserPublic:

    db = session.scalar(
        select(UserModel).where(
            (UserModel.email == user.email)
            | (UserModel.phone_number == user.phone_number)
        )
    )

    if db:
        if db.email == user.email:
            raise HTTPException(409, detail="Email already exists")

        elif db.phone_number == user.phone_number:
            raise HTTPException(409, detail="Phone number already exists")

    db = UserModel(
        name=user.name,
        email=user.email,
        password=hash_password(user.password),
        phone_number=user.phone_number,
    )

    try:
        session.add(db)
        session.commit()
        session.refresh(db)
        return UserPublic.model_validate(db)

    except Exception as e:
        session.rollback()
        print(f"ERROR: {e}")
        raise HTTPException(500, "Internal Error")


# READ
@router.get("/read", status_code=200, response_model=UserList)
async def get_all_users(
    limit: int = 10, offset: int = 0, session: Session = Depends(get_session)
) -> dict:

    try:
        all_users = session.scalars(select(UserModel).limit(limit).offset(offset))
        return {"users": all_users}

    except Exception as e:
        print(f"ERROR: {e}")
        raise HTTPException(500, detail="Internal Error")


@router.get("/read/{user_id}", status_code=200, response_model=UserPublic)
async def get_user_id(
    user_id: int, session: Session = Depends(get_session)
) -> UserPublic:

    try:
        user = session.scalar(select(UserModel).where(UserModel.id == user_id))
        return UserPublic.model_validate(user)

    except Exception as e:
        print(f"ERROR: {e}")
        raise HTTPException(404, detail="User Not Found")


# UPDATE
@router.put("/update/{user_id}", status_code=200, response_model=UserPublic)
async def update_user(
    user_id: int, user: UserCreateSchema, session: Session = Depends(get_session)
) -> UserPublic:

    db = session.scalar(select(UserModel).where(UserModel.id == user_id))
    if not db:
        raise HTTPException(404, detail="User Not Found")

    db.name = user.name
    db.email = user.email
    db.password = hash_password(user.password)
    db.phone_number = user.phone_number

    try:
        session.add(db)
        session.commit()
        session.refresh(db)
        return UserPublic.model_validate(db)

    except IntegrityError:
        session.rollback()
        raise HTTPException(409, detail="Email or Phone Number Already Exists")


# DELETE
@router.delete("/delete/{user_id}", status_code=200)
async def delete_user(user_id: int, session: Session = Depends(get_session)) -> dict:

    db = session.scalar(select(UserModel).where(UserModel.id == user_id))
    if not db:
        raise HTTPException(404, detail=f"User with id: {user_id}, not found")

    try:
        session.delete(db)
        session.commit()
        return {"message": f"User id: {user_id}, deleted from database"}

    except Exception as e:
        session.rollback()
        print(f"ERROR: {e}")
        raise HTTPException(500, detail="Internal Error")


# TOKEN
