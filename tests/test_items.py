import pytest
from fastapi import status
from unittest.mock import patch
from tests.test_utils import (
    assert_response_structure,
    create_user_data,
    create_item_data,
    update_item_data,
)
from app.api.v1.dependencies import get_auth_service


@pytest.fixture
def auth_client(client):
    """
    Automates the full 2-step flow:
    1. Register (Mocking OTP) -> 2. Verify OTP -> 3. Login -> 4. Set Headers
    """
    fixed_otp = "123456"

    user_data = create_user_data()
    with patch(
        "app.service.auth_service.AuthService.generate_otp", return_value=fixed_otp
    ):
        client.post("/users/register", json=user_data)

    client.post(f"/users/verify-otp?email={user_data['email']}&otp={fixed_otp}")

    login_data = {"email": user_data["email"], "password": user_data["password"]}
    response = client.post("/users/login", json=login_data)
    tokens = response.json()["data"]

    client.headers.update({"Authorization": f"Bearer {tokens['access_token']}"})

    return client


# class TestItem:
#     def test_create_item_success(self, auth_client):
#         """Test successful item creation."""
#         item_details = create_item_data()

#         response = auth_client.post("/items/", json=item_details)
#         assert response.status_code == status.HTTP_201_CREATED

#         body = response.json()
#         assert_response_structure(body)

#         assert body["message"] == "Item added successfully."
#         assert body["data"]["title"] == item_details["title"]

#     def test_create_duplicate_item_title_error(self, auth_client):
#         """Test creation of item with an existing title."""
#         item_details = create_item_data(title="unique-title")
#         duplicate_details = create_item_data(
#             title="unique-title", desc="different desc"
#         )

#         auth_client.post("/items/", json=item_details)

#         response = auth_client.post("/items/", json=duplicate_details)
#         assert response.status_code == status.HTTP_409_CONFLICT

#         body = response.json()
#         assert body["detail"] == "Item already exists"

#     def test_edit_item_success(self, auth_client):
#         """Test successful edit item"""
#         item_details = create_item_data()
#         response = auth_client.post("/items/", json=item_details)
#         body = response.json()
#         item_id = body["data"]["id"]

#         update_item_details = update_item_data()
#         response = auth_client.patch(f"/items/{item_id}", json=update_item_details)
#         assert response.status_code == status.HTTP_200_OK

#         body = response.json()
#         assert_response_structure(body)

#         assert body["message"] == "Item updated successfully."
#         assert body["data"]["title"] == update_item_details["title"]
#         assert "desc" in body["data"]

#     def test_delete_item_success(self, auth_client):
#         """Test successful delete item"""
#         item_details = create_item_data()
#         response = auth_client.post("/items/", json=item_details)
#         body = response.json()
#         item_id = body["data"]["id"]

#         response = auth_client.delete(f"/items/{item_id}")
#         assert response.status_code == status.HTTP_200_OK

#         body = response.json()
#         assert_response_structure(body)

#         assert body["message"] == "Item removed successfully."
#         assert body["data"]["title"] == item_details["title"]
#         assert body["data"]["desc"] == item_details["desc"]
