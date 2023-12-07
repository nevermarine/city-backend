from enum import Enum
from uuid import uuid4

import dotenv
# from pydantic import BaseModel, Field
from sqlmodel import Field, SQLModel

config = dotenv.dotenv_values(".env")

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


class Token(SQLModel):
    access_token: str
    token_type: str


class TokenData(SQLModel):
    username: str | None = None


class User(SQLModel, table=True):
    username: str = Field(
        sa_column_kwargs={"unique": True, "nullable": False, "primary_key": True}
    )
    full_name: str = Field(max_length=100)
    email: str = Field(sa_column_kwargs={"unique": True, "nullable": False})


class UserCreate(User):
    password: str


class UserInDB(User):
    password: str


class UserReqStatus(str, Enum):
    pending = "Pending"
    resolved = "Resolved"


class UserRequest(User):
    id: str = Field(default_factory=lambda: uuid4().hex)
    message: str
    status: UserReqStatus = UserReqStatus.pending
    response: str | None = None
