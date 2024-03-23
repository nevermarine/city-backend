import os
import sys

from fastapi.testclient import TestClient

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)

from src.main import app
from src.model import base_models

client = TestClient(app)


# ----------------USERS---------------------
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
        "username": "testuser",
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
    assert type(response.json()) == list


def test_update_user():
    username = "darinka"
    new_user_data = {
        "username": username,
        "email": "newemail@example.com",
        "full_name": "Updated User",
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


def test_update_user_not_found():
    username = "non_existing_user"
    new_user_data = {
        "username": username,
        "email": "newemail@example.com",
        "full_name": "Updated User",
    }
    response = client.put(f"/users/{username}", json=new_user_data)
    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}


def test_login_for_access_token():
    response = client.post("/token", data={"username": "darinka2", "password": "dd"})
    assert response.status_code == 200

    data = response.json()
    assert "access_token" in data
    assert "token_type" in data
    assert data["token_type"] == "bearer"
    assert base_models.Token(**data)


def test_read_users_me():
    response = client.get("/users/me/")
    assert response.status_code == 401

    response = client.post("/token", data={"username": "darinka2", "password": "dd"})

    headers = {"Authorization": f"Bearer {response.json()['access_token']}"}
    response = client.get("/users/me/", headers=headers)
    data = response.json()

    assert response.status_code == 200
    assert "username" in data
    assert "email" in data
    assert "full_name" in data
    assert base_models.Users(**data)


# ----------------USERS REQUESTS---------------------
# ----------------NEWS---------------------
def test_get_news_by_category():
    response = client.get("/news/category/society")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

    for news in response.json():
        assert news["category"] == "society"


# def test_delete_news():
#     news_data = {
#         "date": str(date.today()),
#         "title": "News to Delete",
#         "text": "This is a news to delete",
#         "category": "test_category",
#         "tag": "tag",
#         "page": "example.com",
#     }
#     response = client.post("/news/create", json=news_data)
#     news_id = response.json()["id"]

#     response = client.delete(f"/news/{news_id}")
#     assert response.status_code == 200
#     assert response.json()["message"] == "News deleted successfully"


# def test_get_news_by_id():
#     news_data = {
#         "date": str(date.today()),
#         "title": "News by ID",
#         "text": "This is a news by ID",
#         "category": "test_category",
#         "tag": "tag",
#         "page": "example.com",
#     }
#     response = client.post("/news/create", json=news_data)
#     news_id = response.json()["id"]
#     print(response.json())

#     response = client.get(f"/news/{news_id}")
#     assert response.status_code == 200


def test_get_news():
    response = client.get("/news/")
    assert response.status_code == 200


# ----------------EVENTS---------------------
def test_create_event():
    event_data = {
        "title": "Масленица",
        "location": "New York",
        "description": "Event description here",
        "date": "11-11-2024",
        "time": "18:40",
        "contacts": "some",
        "link": "some",
    }
    response = client.post("/events/create", json=event_data)
    assert response.status_code == 200
    print(response.json())
    assert response.json()["title"] == event_data["title"]


def test_get_events_by_location():
    location = "New York"
    response = client.get(f"/events/location/{location}")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_event_by_id():
    location = "New York"
    response = client.get(f"/events/location/{location}")
    events = response.json()

    event_id = events[0]["id"]
    response = client.get(f"/events/{event_id}")
    assert response.status_code == 200
    assert (
        "id" in response.json()
    )  # Проверяем, что полученный объект события содержит ID


def test_delete_event():
    location = "New York"
    events = client.get(f"/events/location/{location}").json()

    event_id = events[0]["id"]
    response = client.delete(f"/events/{event_id}")
    assert response.status_code == 200
    assert response.json() == {"message": "Event deleted successfully"}


def test_get_events():
    response = client.get("/events")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


# def test_read_own_items():
#     response = client.get("/users/me/items/")
#     assert response.status_code == 401

#     response = client.post("/token", data={"username": "darinka2", "password": "dd"})
#     headers = {"Authorization": f"Bearer {response.json()['access_token']}"}

#     response = client.get("/users/me/items/", headers=headers)
#     assert response.status_code == 200

#     data = response.json()
#     assert isinstance(data, list)
#     assert len(data) > 0
#     item = data[0]
#     assert "item_id" in item
#     assert "owner" in item
