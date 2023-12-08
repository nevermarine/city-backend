import os
import sys

from fastapi.testclient import TestClient

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)

from src.main import app
from src.model import base_models

client = TestClient(app)


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
    assert base_models.Users(**data)


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


def test_create_user():
    user_payload = {
        "username": "testuser",
        "full_name": "Test User",
        "email": "testuser@example.com",
        "password": "secretpass",
    }

    response = client.post("/users/create", json=user_payload)
    assert response.status_code == 200

    created_user = response.json()
    assert "username" in created_user
    assert "full_name" in created_user
    assert "email" in created_user
    assert created_user["username"] == user_payload["username"]


def test_create_existing_user():
    user_payload = {
        "username": "darinka",
        "full_name": "Test User",
        "email": "testuser@example.com",
        "password": "secretpass",
    }
    response = client.post("/users/create", json=user_payload)
    assert response.status_code == 404
    assert response.json()["detail"] == "User already exist"


def test_delete_user():
    username = "testuser"

    response = client.delete(f"/users/{username}")
    assert response.status_code == 200

    deleted_user = response.json()
    assert "username" in deleted_user
    assert "full_name" in deleted_user
    assert "email" in deleted_user
    assert deleted_user["username"] == username


def test_delete_user_not_found():
    client = TestClient(app)
    username = "nonexistent_user"

    response = client.delete(f"/users/{username}")

    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}


def test_get_all_users():
    response = client.get("/users")
    assert response.status_code == 200
    assert len(response.json()) == len(base_models.fake_users_db)


def test_update_user():
    username = "darinka"
    new_user_data = {
        "username": username,
        "email": "newemail@example.com",
        "full_name": "Updated User",
        "disabled": True,
    }

    response = client.put(f"/users/{username}", json=new_user_data)
    assert response.status_code == 200

    updated_user = response.json()
    assert "username" in updated_user
    assert "full_name" in updated_user
    assert "email" in updated_user
    assert updated_user["username"] == username
    assert updated_user["full_name"] == new_user_data["full_name"]
    assert updated_user["email"] == new_user_data["email"]
    assert updated_user["disabled"] == new_user_data["disabled"]


def test_update_user_not_found():
    username = "non_existing_user"
    new_user_data = {
        "username": username,
        "email": "newemail@example.com",
        "full_name": "Updated User",
        "disabled": True,
    }
    response = client.put(f"/users/{username}", json=new_user_data)
    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}
