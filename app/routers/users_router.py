from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.db_config import get_session
from app.models.user_model import UserModel
from app.schemas.users_schema import UserCreateSchema, UserList, UserPublic
from app.services.user_services import UserService
from app.utils.hash_password import hash_password
from app.utils.token import get_current_user

router = APIRouter(prefix="/users", tags=["users"])


def user_service(session: Session = Depends(get_session)) -> UserService:
    return UserService(session)


# CREATE
@router.post("/create", status_code=201, response_model=UserPublic)
async def create_user(
    user_data: UserCreateSchema, service: UserService = Depends(user_service)
):  # -> UserPublic:

    try:
        return service.create_user(user_data)

    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))

    except Exception:
        raise HTTPException(status_code=500, detail="Internal Error")


# READ
@router.get("/read", status_code=200, response_model=UserList)
async def get_all_users(
    limit: int = 10,
    offset: int = 0,
    service: UserService = Depends(user_service),
    current_user=Depends(get_current_user),
) -> dict:

    try:
        all_users = service.list_users(limit, offset)
        return {"users": all_users}
    except Exception as e:
        print(f"ERROR: {e}")
        raise HTTPException(500, detail="Internal Error")


@router.get("/read/{user_id}", status_code=200, response_model=UserPublic)
async def get_user_id(
    user_id: int, service: UserService = Depends(user_service)
) -> UserPublic:

    try:
        user = service.find_by_id(user_id)
        return UserPublic.model_validate(user)

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    except Exception as e:
        print(f"Unexpected Error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


# UPDATE
@router.put("/update/{user_id}", status_code=200, response_model=UserPublic)
async def update_user(
    user_id: int,
    user: UserCreateSchema,
    service: UserService = Depends(user_service),
    current_user: UserModel = Depends(get_current_user),
):  # -> UserPublic:

    if current_user.id != user_id:
        raise HTTPException(403, detail="Not Enough Permissions")

    try:
        return service.update_user(user, user_id)

    except Exception as e:
        raise e


# DELETE
@router.delete("/delete/{user_id}", status_code=200)
async def delete_user(
    user_id: int,
    session: Session = Depends(get_session),
    current_user=Depends(get_current_user),
    service: UserService = Depends(user_service),
) -> dict:

    if current_user.id != user_id:
        raise HTTPException(403, detail="Not Enough Permissions")

    try:
        return service.user_delete(current_user)

    except Exception as e:
        session.rollback()
        print(f"ERROR: {e}")
        raise HTTPException(500, detail="Internal Error")
