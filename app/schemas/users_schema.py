from pydantic import BaseModel, ConfigDict, EmailStr


# schema to create users
class UserCreateSchema(BaseModel):
    name: str
    email: EmailStr
    password: str
    phone_number: str | None


# this schema omit the password and add the id
class UserPublic(BaseModel):
    id: int
    name: str
    email: EmailStr
    phone_number: str | None

    model_config = ConfigDict(from_attributes=True)


# schema to list all users
class UserList(BaseModel):
    users: list[UserPublic]


class Token(BaseModel):
    access_token: str
    token_type: str
