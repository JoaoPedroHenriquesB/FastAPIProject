from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database.db_config import get_session
from app.models.user_model import UserModel
from app.schemas.users_schema import UserCreateSchema, UserList, UserPublic
from app.utils.hash_password import hash_password
from app.utils.token import get_current_user

router = APIRouter(prefix="/users", tags=["users"])


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
    limit: int = 10,
    offset: int = 0,
    session: Session = Depends(get_session),
    current_user=Depends(get_current_user),
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
    user_id: int,
    user: UserCreateSchema,
    session: Session = Depends(get_session),
    current_user: UserModel = Depends(get_current_user),
) -> UserPublic:

    if current_user.id != user_id:
        raise HTTPException(403, detail="Not Enough Permissions")

    try:
        current_user.name = user.name
        current_user.email = user.email
        current_user.password = hash_password(user.password)
        current_user.phone_number = user.phone_number

        session.add(current_user)
        session.commit()
        session.refresh(current_user)
        
        return UserPublic.model_validate(current_user)

    except:
        session.rollback()
        raise HTTPException(409, detail="Email or Phone Number Already Exists")


# DELETE
@router.delete("/delete/{user_id}", status_code=200)
async def delete_user(
    user_id: int,
    session: Session = Depends(get_session),
    current_user=Depends(get_current_user),
) -> dict:

    if current_user.id != user_id:
        raise HTTPException(403, detail="Not Enough Permissions")

    try:
        session.delete(current_user)
        session.commit()
        return {"message": f"User id: {user_id}, deleted from database"}

    except Exception as e:
        session.rollback()
        print(f"ERROR: {e}")
        raise HTTPException(500, detail="Internal Error")
