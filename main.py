from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from typing import Annotated

from model import base_models
from auth import auth
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
import argparse
import json

app = FastAPI()


@app.post("/token", response_model=base_models.Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    user = auth.authenticate_user(base_models.fake_users_db, form_data.username, form_data.password)
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


@app.get("/users/me/", response_model=base_models.User)
async def read_users_me(
    current_user: Annotated[base_models.User, Depends(auth.get_current_active_user)]
):
    return current_user

@app.get("/users/me/items/")
async def read_own_items(
    current_user: Annotated[base_models.User, Depends(auth.get_current_active_user)]
):
    return [{"item_id": "Foo", "owner": current_user.username}]

# @app.get("/user_reqs/me/items")
# async def read_own_user_reqs(
#     current_user: Annotated[base_models.User, Depends(auth.get_current_active_user)],
#     id: 
# )
# @app.get("/user_reqs/items")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", type=str, default=None, help="host name")
    parser.add_argument("--port", type=int, default=5000, help="port number")
    parser.add_argument("--allow-credentials",
                        action="store_true",
                        help="allow credentials")
    parser.add_argument("--allowed-origins",
                        type=json.loads,
                        default=["*"],
                        help="allowed origins")
    parser.add_argument("--allowed-methods",
                        type=json.loads,
                        default=["*"],
                        help="allowed methods")
    parser.add_argument("--allowed-headers",
                        type=json.loads,
                        default=["*"],
                        help="allowed headers")
    args = parser.parse_args()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=args.allowed_origins,
        allow_credentials=args.allow_credentials,
        allow_methods=args.allowed_methods,
        allow_headers=args.allowed_headers,
    )
    
    uvicorn.run(app, port=5000, log_level="info")
