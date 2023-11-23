from typing import Annotated

from passlib.hash import bcrypt
from pydantic import BaseModel

HASHED_PASS = bcrypt.hash("secret")


fake_users_db = {
    "darinka": {
        "username": "darinka",
        "full_name": "Darina Rustamova",
        "email": "darinka@rustamova.ru",
        "hashed_password": HASHED_PASS,
        "disabled": False,
    },
    "maxim": {
        "username": "maxim",
        "full_name": "Maxim Fedotov",
        "email": "maxim@fedotov.ru",
        "hashed_password": HASHED_PASS,
        "disabled": False,
    },
}


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class User(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None


class UserInDB(User):
    hashed_password: str
