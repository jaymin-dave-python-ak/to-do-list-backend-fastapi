from fastapi import status
from app.api.v1.schemas.response import create_response


def test_root(client):
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK

    expected_data = create_response([], "Server is running!").model_dump()
    assert response.json() == expected_data
