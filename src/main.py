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
from sqlmodel import Session, delete, select, update

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


@app.get("/users/me/items/")
async def read_own_items(
    current_user: Annotated[base_models.Users, Depends(auth.get_current_active_user)]
):
    with Session(engine) as session:
        statement = select(base_models.UserRequest).where(
            base_models.UserRequest.username == current_user.username
        )
        requests = session.exec(statement).all()

    return requests


@app.get("/user_reqs/items/id/", response_model=base_models.UserRequest)
async def read_own_user_reqs_by_id(
    id_request: str,
):
    with Session(engine) as session:
        statement = select(base_models.UserRequest).where(
            base_models.UserRequest.id == id_request
        )
        request_info = session.exec(statement).first()

    return request_info


@app.post("/user_reqs/create/", response_model=base_models.UserRequest)
async def create_user_request(
    request: base_models.UserRequest,
    current_user: Annotated[base_models.Users, Depends(auth.get_current_active_user)],
):
    request.username = current_user.username

    with Session(engine) as session:
        session.add(request)
        session.commit()
        session.refresh(request)

    return request


@app.put("/user_reqs/{id_request}/status/")
async def update_user_request_status(
    id_request: str, status: base_models.UserReqStatus
):
    with Session(engine) as session:
        statement = (
            update(base_models.UserRequest)
            .where(base_models.UserRequest.id == id_request)
            .values(status=status)
        )

        session.exec(statement)
        session.commit()

    return {"message": "Status updated successfully"}


@app.put("/user_reqs/{id_request}/response/")
async def add_user_request_response(id_request: str, response: str):
    with Session(engine) as session:
        statement = (
            update(base_models.UserRequest)
            .where(base_models.UserRequest.id == id_request)
            .values(response=response)
        )

        session.exec(statement)
        session.commit()

    return {"message": "Response added successfully"}


@app.delete("/user_reqs/{id_request}/")
async def delete_user_request(id_request: str):
    with Session(engine) as session:
        statement = delete(base_models.UserRequest).where(
            base_models.UserRequest.id == id_request
        )

        session.exec(statement)
        session.commit()

    return {"message": "User request deleted successfully"}


@app.get("/user_reqs/{username}/items/", response_model=list[base_models.UserRequest])
async def get_user_requests(username: str):
    with Session(engine) as session:
        statement = select(base_models.UserRequest).where(
            base_models.UserRequest.username == username
        )
        user_requests = session.exec(statement).all()

    return user_requests


@app.post("/news/create")
async def create_news(
    news: base_models.News,
):
    with Session(engine) as session:
        session.add(news)
        session.commit()

    return {"message": "News created successfully"}


@app.get("/news/{category}")
async def get_news_by_category(category: str):
    with Session(engine) as session:
        statement = select(base_models.News).where(
            base_models.News.category == category
        )
        news_list = session.exec(statement).all()

    return news_list


@app.delete("/news/{news_id}")
async def delete_news(news_id: str):
    with Session(engine) as session:
        statement = delete(base_models.News).where(base_models.News.id == news_id)
        session.exec(statement)

    return {"message": "News deleted successfully"}


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
