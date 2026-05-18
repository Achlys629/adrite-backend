import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_register():
    response = client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Test User",
            "email": "testuser@gmail.com",
            "password": "Test@1234"
        }
    )
    assert response.status_code == 200
    assert response.json()["email"] == "testuser@gmail.com"

def test_login():
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "testuser@gmail.com",
            "password": "Test@1234"
        }
    )
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_login_wrong_password():
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "testuser@gmail.com",
            "password": "wrongpassword"
        }
    )
    assert response.status_code == 401

def test_get_me_without_token():
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 403