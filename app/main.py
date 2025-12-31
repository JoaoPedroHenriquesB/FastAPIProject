from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.routers.auth_router import auth_router
from app.routers.task_router import task_router
from app.routers.user_router import user_router
from app.utils.exceptions import (
    InternalDomainError,
    NotFoundError,
    PermissionDeniedError,
)

app = FastAPI(title="My First API")


@app.exception_handler(NotFoundError)
async def not_found_exception_handler(request: Request, exc: NotFoundError):
    return JSONResponse(
        status_code=404,
        content={"message": "the requested item is not found"},
    )


@app.exception_handler(PermissionDeniedError)
async def permission_denied_handler(request: Request, exc: PermissionDeniedError):
    return JSONResponse(
        status_code=403,
        content={"message": "you are not allowed to perform this action."},
    )


@app.exception_handler(InternalDomainError)
async def internal_error_handler(request: Request, exc: InternalDomainError):
    return JSONResponse(
        status_code=500,
        content={"message": "internal server error ocurred."},
    )


app.include_router(auth_router)
app.include_router(user_router)
app.include_router(task_router)


@app.get("/")
async def main():
    return {"message": "Hello World"}
