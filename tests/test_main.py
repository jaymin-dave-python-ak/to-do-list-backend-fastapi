from fastapi import status
from tests.test_utils import assert_response_structure


async def test_root_success(client):
    """Test root endpoint."""
    response = await client.get("/")

    assert response.status_code == status.HTTP_200_OK

    body = response.json()
    assert_response_structure(body)

    assert body["message"] == "Server is running!"
    assert body["data"] == []
