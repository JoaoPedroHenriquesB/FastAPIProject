from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jwt import decode, encode
from sqlalchemy import select
from sqlalchemy.orm import Session

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


oauth2_schema = OAuth2PasswordBearer(tokenUrl="auth/token")


def get_current_user(
    session: Session = Depends(get_session), token: str = Depends(oauth2_schema)
):

    credentials_exception = HTTPException(
        401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        subject_email = payload.get("sub")

        if not subject_email:
            raise credentials_exception

    except Exception:
        raise credentials_exception

    user = session.scalar(select(UserModel).where(UserModel.email == subject_email))
    if not user:
        raise credentials_exception

    return user
