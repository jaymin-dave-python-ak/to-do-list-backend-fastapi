import pytest
from fastapi import status
from app.api.v1.dependencies import auth_service
from tests.test_utils import (
    assert_response_structure,
    create_user_data,
    create_item_data,
    update_item_data,
)


@pytest.fixture
def auth_client(client):
    """Creates a user and authenticates the client for item tests."""
    user_details = create_user_data(email="item-tester@gmail.com")
    response = client.post("/users/register", json=user_details)
    user_id = response.json()["data"]["id"]

    token = auth_service.create_access_token(data={"sub": str(user_id)})

    client.headers.update({"Authorization": f"Bearer {token}"})

    return client


class TestItem:
    def test_create_item_success(self, auth_client):
        """Test successful item creation."""
        item_details = create_item_data()

        response = auth_client.post("/items/", json=item_details)
        assert response.status_code == status.HTTP_201_CREATED

        body = response.json()
        assert_response_structure(body)

        assert body["message"] == "Item added successfully."
        assert body["data"]["title"] == item_details["title"]

    def test_create_duplicate_item_title_error(self, auth_client):
        """Test creation of item with an existing title."""
        item_details = create_item_data(title="unique-title")
        duplicate_details = create_item_data(
            title="unique-title", desc="different desc"
        )

        auth_client.post("/items/", json=item_details)

        response = auth_client.post("/items/", json=duplicate_details)
        assert response.status_code == status.HTTP_409_CONFLICT

        body = response.json()
        assert body["detail"] == "Item already exists"

    def test_edit_item_success(self, auth_client):
        """Test successful edit item"""
        item_details = create_item_data()
        response = auth_client.post("/items/", json=item_details)
        body = response.json()
        item_id = body["data"]["id"]

        update_item_details = update_item_data()
        response = auth_client.patch(f"/items/{item_id}", json=update_item_details)
        assert response.status_code == status.HTTP_200_OK

        body = response.json()
        assert_response_structure(body)

        assert body["message"] == "Item updated successfully."
        assert body["data"]["title"] == update_item_details["title"]
        assert "desc" in body["data"]

    def test_delete_item_success(self, auth_client):
        """Test successful delete item"""
        item_details = create_item_data()
        response = auth_client.post("/items/", json=item_details)
        body = response.json()
        item_id = body["data"]["id"]

        response = auth_client.delete(f"/items/{item_id}")
        assert response.status_code == status.HTTP_200_OK

        body = response.json()
        assert_response_structure(body)

        assert body["message"] == "Item removed successfully."
        assert body["data"]["title"] == item_details["title"]
        assert body["data"]["desc"] == item_details["desc"]