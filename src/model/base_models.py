import enum
import uuid
from datetime import date, datetime
from typing import List, Optional

import dotenv
from pydantic import UUID4, BaseModel
from sqlmodel import Column, Enum, Field, Relationship, SQLModel

config = dotenv.dotenv_values(".env")


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
    requests: List["UserRequest"] = Relationship(
        back_populates="user", sa_relationship_kwargs={"cascade": "delete"}
    )
    admin: bool = False


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


class UserReqStatus(str, enum.Enum):
    pending = "Pending"
    resolved = "Resolved"


def new_uuid() -> uuid.UUID:
    # Note: Work around UUIDs with leading zeros: https://github.com/tiangolo/sqlmodel/issues/25
    # by making sure uuid str does not start with a leading 0
    val = uuid.uuid4()
    while val.hex[0] == "0":
        val = uuid.uuid4()
    return val


class News(SQLModel, table=True):
    id: UUID4 = Field(
        unique=True, nullable=False, primary_key=True, default_factory=new_uuid
    )
    date: datetime = Field(default_factory=date.today)
    title: str = Field(nullable=False)
    category: str = Field(nullable=False)
    page: str = Field(nullable=False)


class UserRequest(SQLModel, table=True):
    id: UUID4 = Field(
        unique=True, nullable=False, primary_key=True, default_factory=new_uuid
    )
    username: str = Field(nullable=False, foreign_key="users.username")
    message: str = Field(nullable=False)
    status: UserReqStatus = Field(
        sa_column=Column(Enum(UserReqStatus)), default=UserReqStatus.pending
    )
    response: str = Field(nullable=True)
    date: datetime = Field(default_factory=datetime.now)

    user: Users = Relationship(back_populates="requests")
