from typing import Optional

from pydantic import BaseModel

from model import base_models


async def get_user_req_by_id(db, id: str) -> Union[base_models.UserRequest]:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    user_req = db.get(id, None)
    if user_req is None:
        raise credentials_exception
    return user_req
