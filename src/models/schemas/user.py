import datetime

import pydantic

from src.models.schemas.base import BaseSchemaModel


class UserInCreate(BaseSchemaModel):
    username: str
    email: pydantic.EmailStr
    password: str


class UserInUpdate(BaseSchemaModel):
    username: str | None
    email: str | None
    password: str | None


class UserInLogin(BaseSchemaModel):
    username: str
    email: pydantic.EmailStr
    password: str


class UserWithToken(BaseSchemaModel):
    token: str
    username: str
    email: pydantic.EmailStr
    is_verified: bool
    is_active: bool
    is_logged_in: bool
    created_at: datetime.datetime
    updated_at: datetime.datetime | None


class UserInResponse(BaseSchemaModel):
    id: int
    authorized_user: UserWithToken