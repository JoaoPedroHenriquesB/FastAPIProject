from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.db_config import get_session
from app.models.user_model import UserModel
from app.schemas.users_schema import UserCreateSchema, UserList, UserPublic
from app.services.user_services import UserService
from app.utils.token import get_current_user, requires_admin
from app.utils.misc import FilterPage
user_router = APIRouter(prefix="/users", tags=["users"])


def user_service(session: AsyncSession = Depends(get_session)) -> UserService:
    return UserService(session)


T_Service = Annotated[UserService, Depends(user_service)]
T_CurrentUser = Annotated[UserModel, Depends(get_current_user)]
T_FilterPage = Annotated[FilterPage, Query()]
T_Admin = Annotated[UserModel, Depends(requires_admin)]


# CREATE
@user_router.post("/create", status_code=201, response_model=UserPublic)
async def create_user(user_data: UserCreateSchema, service: T_Service):  # -> UserPublic:
    try:
        return await service.create_user(user_data)

    except ValueError as e:
        print(f"ERROR: {e}")
        raise HTTPException(500, detail="Internal Error")

    except Exception as e:
        print(f"ERROR: {e}")
        raise HTTPException(500, detail="Internal Error")


# READ
@user_router.get("/read", status_code=200, response_model=UserList)
async def get_all_users(
    service: T_Service, admin: T_Admin, filter_get: T_FilterPage
)-> dict:

    try:
        all_users = await service.list_users(filter_get.limit, filter_get.offset)
        return {"users": all_users}

    except Exception as e:
        print(f"ERROR: {e}")
        raise HTTPException(500, detail="Internal Error")


@user_router.get("/read/{user_id}", status_code=200, response_model=UserPublic)
async def get_user_id(
    user_id: int, service: T_Service, admin: T_Admin
) -> UserPublic:
    try:
        user = await service.find_by_id(user_id)
        return UserPublic.model_validate(user)

    except ValueError as e:
        print(f"ERROR: {e}")
        raise HTTPException(500, detail="Internal Error")

    except Exception as e:
        print(f"ERROR: {e}")
        raise HTTPException(500, detail="Internal Error")


# UPDATE
@user_router.put("/update/{user_id}", status_code=200, response_model=UserPublic)
async def update_user(
    user_id: int,
    user: UserCreateSchema,
    service: T_Service,
    current_user: T_CurrentUser,
    admin: T_Admin
):  # -> UserPublic:

    if current_user.id != user_id:
        raise HTTPException(403, detail="Not Enough Permissions")

    try:
        return await service.update_user(user, user_id)

    except Exception as e:
        print(f"ERROR: {e}")
        raise HTTPException(500, detail="Internal Error")


# DELETE
@user_router.delete("/delete/{user_id}", status_code=200)
async def delete_user(
    admin: T_Admin,
    service: T_Service,
    user_id: int,
) -> dict:

    await service.user_delete(user_id)

    try:
        return {"message": "user deleted by " + admin.name}

    except Exception as e:
        print(f"ERROR: {e}")
        raise HTTPException(500, detail="Internal Error")
