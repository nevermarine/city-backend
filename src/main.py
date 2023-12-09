import argparse
import json
import logging
from datetime import timedelta
from typing import Annotated

import uvicorn
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from passlib.hash import bcrypt
from sqlmodel import Session, select

from src.auth import auth
from src.model import base_models
from src.model.conn import engine

app = FastAPI(debug=True)


def check_exist_user(username: str):
    with Session(engine) as session:
        statement = select(base_models.Users).where(
            base_models.Users.username == username
        )
        find_user = session.exec(statement).first()

    return find_user


@app.post("/token", response_model=base_models.Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    user = auth.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me/", response_model=base_models.Users)
async def read_users_me(
    current_user: Annotated[base_models.Users, Depends(auth.get_current_active_user)]
):
    return current_user


@app.get("/users/me/items/")
async def read_own_items(
    current_user: Annotated[base_models.Users, Depends(auth.get_current_active_user)]
):
    return [{"item_id": "Foo", "owner": current_user.username}]


@app.post("/users/create", response_model=base_models.Users)
async def create_user(user: base_models.UserCreate):
    with Session(engine) as session:
        statement = select(base_models.Users).where(
            base_models.Users.username == user.username
        )
        find_user = session.exec(statement).first()

        if find_user is None:
            user_data = user.model_dump()
            hashed_password = bcrypt.hash(user_data["password"])

            new_user_json = {
                "username": user_data["username"],
                "full_name": user_data["full_name"],
                "email": user_data["email"],
            }
            new_pass_user_json = {
                "username": user_data["username"],
                "password": hashed_password,
            }

            new_user = base_models.Users(**new_user_json)
            session.add(new_user)
            session.commit()

            new_pass_user = base_models.Passwords(**new_pass_user_json)
            session.add(new_pass_user)
            session.commit()

            return base_models.Users(**new_user_json)

        else:
            raise HTTPException(status_code=404, detail="User already exist")


@app.delete("/users/{username}", response_model=base_models.Users)
async def delete_user(username: str):
    with Session(engine) as session:
        statement = select(base_models.Users).where(
            base_models.Users.username == username
        )
        find_user = session.exec(statement).first()

        if find_user is not None:
            session.delete(find_user)
            session.commit()
            return find_user
        else:
            raise HTTPException(status_code=404, detail="User not found")


@app.get("/users", response_model=list[base_models.Users])
async def get_all_users():
    with Session(engine) as session:
        statement = select(base_models.Users)
        users = session.exec(statement).all()
    return users


@app.put("/users/{username}", response_model=base_models.Users)
async def update_user(username: str, new_user_data: base_models.Users):
    find_user = check_exist_user(username)
    if find_user is not None:
        with Session(engine) as session:
            logging.info(find_user)
            find_user.email = new_user_data.email
            find_user.full_name = new_user_data.full_name
            session.add(find_user)
            session.commit()
            session.refresh(find_user)
            return find_user
    else:
        raise HTTPException(status_code=404, detail="User not found")


@app.get("/user_reqs/items/id/", response_model=base_models.UserRequest)
async def read_own_user_reqs_by_id(
    current_user: Annotated[base_models.Users, Depends(auth.get_current_active_user)],
    id: str,
):
    user_req = base_models.fake_user_reqs_db.get(id)
    if user_req is None or user_req["username"] != current_user.username:
        raise HTTPException(status_code=404, detail="Item not found")
    return user_req


@app.get("/user_reqs/items/me/", response_model=list[base_models.UserRequest])
async def read_own_user_reqs(
    current_user: Annotated[base_models.Users, Depends(auth.get_current_active_user)],
):
    filtered_dict = {
        key: value
        for key, value in base_models.fake_user_reqs_db.items()
        if value["username"] == current_user.username
    }
    if filtered_dict is {}:
        raise HTTPException(status_code=404, detail="Item not found")
    return filtered_dict.values()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", type=str, default="0.0.0.0", help="host name")
    parser.add_argument("--port", type=int, default=5000, help="port number")
    parser.add_argument(
        "--allow-credentials", action="store_true", help="allow credentials"
    )
    parser.add_argument(
        "--allowed-origins", type=json.loads, default=["*"], help="allowed origins"
    )
    parser.add_argument(
        "--allowed-methods", type=json.loads, default=["*"], help="allowed methods"
    )
    parser.add_argument(
        "--allowed-headers", type=json.loads, default=["*"], help="allowed headers"
    )
    args = parser.parse_args()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=args.allowed_origins,
        allow_credentials=args.allow_credentials,
        allow_methods=args.allowed_methods,
        allow_headers=args.allowed_headers,
    )

    uvicorn.run(app, port=args.port, host=args.host, log_level="info")
