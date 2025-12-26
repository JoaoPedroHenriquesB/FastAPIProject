from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jwt import DecodeError, ExpiredSignatureError, decode, encode
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import settings
from app.database.db_config import get_session
from app.models.user_model import UserModel

SECRET_KEY = settings.SECRET_KEY
TOKEN_EXPIRE = settings.TOKEN_EXPIRE
ALGORITHM = settings.ALGORITHM


def create_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(tz=ZoneInfo("UTC")) + timedelta(minutes=TOKEN_EXPIRE)
    to_encode.update({"exp": expire})

    encoded_jwt = encode(to_encode, SECRET_KEY, ALGORITHM)
    return encoded_jwt


oauth2_schema = OAuth2PasswordBearer(
    tokenUrl="auth/token", refreshUrl="auth/refresh_token"
)


async def get_current_user(
    session: AsyncSession = Depends(get_session), token: str = Depends(oauth2_schema)
):
    try:
        payload = decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")

        if not email:
            raise HTTPException(
                status_code=401, detail="Could not validate credentials"
            )

    except DecodeError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")

    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token already expired")

    user = await session.scalar(select(UserModel).where(UserModel.email == email))

    if not user:
        raise HTTPException(401, detail="User not found")

    return user


async def requires_admin(current_user: UserModel = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(
            status_code=403, detail="Acesso negado: Requer privilégios de ADMIN"
        )
    return current_user
