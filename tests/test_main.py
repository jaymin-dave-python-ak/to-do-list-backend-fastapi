from fastapi import status
from tests.utils import assert_response_structure


def test_root(client):
    """Verify that the root endpoint returns server running response."""
    response = client.get("/")

    assert response.status_code == status.HTTP_200_OK

    body = response.json()
    assert_response_structure(body)

    assert body["message"] == "Server is running!"
    assert body["data"] == []


def test_register_user_success(client):
    """Test successful user registration with valid user details."""

    user_details = {
        "email": "test-user@gmail.com",
        "username": "test-user",
        "is_active": True,
        "is_admin": False,
        "password": "test-user123"
    }

    response = client.post("/users/register", json=user_details)

    assert response.status_code == status.HTTP_201_CREATED

    body = response.json()
    assert_response_structure(body)

    assert body["message"] == "User registered successfully."
    assert body["data"]["email"] == user_details["email"]
    assert "id" in body["data"]
    assert "password" not in body["data"]


def test_register_duplicate_email(client):
    """Test that registering with an already existing email returns a 400 error."""

    user_details = {
        "email": "duplicate@gmail.com",
        "username": "duplicate-user",
        "is_active": True,
        "is_admin": False,
        "password": "duplicate123"
    }

    # First registration
    client.post("/users/register", json=user_details)

    # Second registration
    response = client.post("/users/register", json=user_details)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "Email already registered"


def test_login_success(client):
    """Test successful login and JWT access token generation."""

    user_details = {
        "email": "login-user@gmail.com",
        "username": "login-user",
        "is_active": True,
        "is_admin": False,
        "password": "login123"
    }

    # Register user
    client.post("/users/register", json=user_details)

    login_payload = {
        "email": "login-user@gmail.com",
        "password": "login123"
    }

    response = client.post("/users/login", json=login_payload)

    assert response.status_code == status.HTTP_200_OK

    body = response.json()
    assert_response_structure(body)

    assert body["message"] == "Login successful."
    assert "access_token" in body["data"]
    assert body["data"]["token_type"] == "bearer"


def test_login_invalid_password(client):
    """Test login failure when incorrect password is provided."""

    user_details = {
        "email": "wrong-pass@gmail.com",
        "username": "wrong-pass",
        "is_active": True,
        "is_admin": False,
        "password": "correctpass"
    }

    # Register user
    client.post("/users/register", json=user_details)

    login_payload = {
        "email": "wrong-pass@gmail.com",
        "password": "incorrectpass"
    }

    response = client.post("/users/login", json=login_payload)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Invalid credentials"