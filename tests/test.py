from fastapi.testclient import TestClient
from passlib.hash import bcrypt

from src.main import app
from src.model import base_models

client = TestClient(app)

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))


def test_login_for_access_token():
    response = client.post("/token", data={"username": "darinka", "password": "secret"})
    assert response.status_code == 200

    data = response.json()
    assert "access_token" in data
    assert "token_type" in data
    assert data["token_type"] == "bearer"
    assert base_models.Token(**data)


def test_read_users_me():
    response = client.get("/users/me/")
    assert response.status_code == 401

    response = client.post("/token", data={"username": "darinka", "password": "secret"})

    headers = {"Authorization": f"Bearer {response.json()['access_token']}"}
    response = client.get("/users/me/", headers=headers)
    data = response.json()

    assert response.status_code == 200
    assert "username" in data
    assert "email" in data
    assert "full_name" in data
    assert "disabled" in data
    assert base_models.User(**data)


def test_read_own_items():
    response = client.get("/users/me/items/")
    assert response.status_code == 401

    response = client.post("/token", data={"username": "darinka", "password": "secret"})
    headers = {"Authorization": f"Bearer {response.json()['access_token']}"}

    response = client.get("/users/me/items/", headers=headers)
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    item = data[0]
    assert "item_id" in item
    assert "owner" in item
