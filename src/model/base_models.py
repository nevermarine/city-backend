from enum import Enum
from typing import Annotated
from uuid import uuid4
from passlib.hash import bcrypt
from pydantic import BaseModel, Field

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

fake_user_reqs_db = {
    "a5cf4789b6f74285b820e754f4ed65bb": {
        "id": "a5cf4789b6f74285b820e754f4ed65bb",
        "username": "maxim",
        "message": "Как мне сняться с учета в военкомате?",
        "status": "Pending",
    },
    "6196a6cd7a3b4d77a8964c8a5efad8ab": {
        "id": "6196a6cd7a3b4d77a8964c8a5efad8ab",
        "username": "darinka",
        "message": "Где в городе находится центр госуслуг?",
        "status": "Resolved",
        "response": "Здравствуйте, Дарина! Ближайший центр госуслуг находится в г. Навои.",
    },
    "41694f46d89046f689fdb119ff62de23": {
        "id": "41694f46d89046f689fdb119ff62de23",
        "username": "maxim",
        "message": "Сколько стоят жвачки по рублю?",
        "status": "Resolved",
        "response": "Здравствуйте, Максим! Жвачки по рублю стоят 2 рубля.",
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


class UserReqStatus(str, Enum):
    pending = "Pending"
    resolved = "Resolved"


class UserRequest(User):
    id: str = Field(default_factory=lambda: uuid4().hex)
    message: str
    status: UserReqStatus = UserReqStatus.pending
    response: str | None = None
