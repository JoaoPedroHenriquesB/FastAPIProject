from fastapi import FastAPI

from app.routers.auth_router import auth_router
from app.routers.user_router import user_router

app = FastAPI(title="My First APP")

app.include_router(auth_router)
app.include_router(user_router)


@app.get("/")
async def main():
    return {"message": "Hello World"}
