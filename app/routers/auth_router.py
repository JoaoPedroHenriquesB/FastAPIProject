from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.db_config import get_session
from app.models.user_model import UserModel
from app.schemas.users_schema import Token
from app.utils.hash_password import verify_password
from app.utils.token import create_token, get_current_user

auth_router = APIRouter(prefix="/auth", tags=["auth"])

OAuth2 = Annotated[OAuth2PasswordRequestForm, Depends()]
T_Session = Annotated[AsyncSession, Depends(get_session)]  # T = Type, Type_Session
T_CurrentUser = Annotated[UserModel, Depends(get_current_user)]


@auth_router.post("/token", response_model=Token)
async def login_token(session: T_Session, form_data: OAuth2):

    user = await session.scalar(
        select(UserModel).where(UserModel.email == form_data.username)
    )

    if not user:
        raise HTTPException(status_code=401, detail="Incorrect Email or Password")

    if not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=401, detail="Incorrect Email or Password")

    access_token = create_token({"sub": user.email, "is_admin": user.is_admin})
    return {"access_token": access_token, "token_type": "Bearer"}


@auth_router.post("/refresh_token", response_model=Token)
async def refresh_token(user: T_CurrentUser):
    new_token = create_token(data={"sub": user.email, "is_admin": user.is_admin})

    return {"access_token": new_token, "token_type": "bearer"}
