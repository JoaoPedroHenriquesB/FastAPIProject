from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from schemas.users_schema import Token
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.db_config import get_session
from app.models.user_model import UserModel
from app.routers.users_router import router
from app.utils.hash_password import hash_password, verify_password

app = FastAPI(title="My First API")
app.include_router(router)


@app.get("/")
async def main():
    return {"message": "Hello World"}


@app.post("/token", response_model=Token)
async def login_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
):

    user = session.scalar(
        select(UserModel).where(UserModel.email == form_data.username)
    )

    if not user:
        raise HTTPException(401, detail="Incorrect Email or Password")

    if not verify_password(form_data.password, user.password):
        raise HTTPException(401, detail="Incorrect Email or Password")
