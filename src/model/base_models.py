from enum import Enum
from typing import List, Optional
from uuid import uuid4

import dotenv
from pydantic import BaseModel
from sqlmodel import Field, Relationship, SQLModel

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


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class Users(SQLModel, table=True):
    username: str = Field(unique=True, nullable=False, primary_key=True)
    full_name: Optional[str] = Field(max_length=100)
    email: Optional[str] = Field(unique=True, nullable=False)

    password: List["Passwords"] = Relationship(
        back_populates="info", sa_relationship_kwargs={"cascade": "delete"}
    )


class UserCreate(BaseModel):
    username: str = Field(unique=True, nullable=False, primary_key=True)
    full_name: Optional[str] = Field(max_length=100)
    email: Optional[str] = Field(unique=True, nullable=False)
    password: str


class Passwords(SQLModel, table=True):
    username: str = Field(
        unique=True, nullable=False, primary_key=True, foreign_key="users.username"
    )
    password: str = Field(nullable=True)

    info: Users = Relationship(back_populates="password")


class UserReqStatus(str, Enum):
    pending = "Pending"
    resolved = "Resolved"


class UserRequest(BaseModel):
    id: str = Field(default_factory=lambda: uuid4().hex)
    message: str
    status: UserReqStatus = UserReqStatus.pending
    response: str | None = None
