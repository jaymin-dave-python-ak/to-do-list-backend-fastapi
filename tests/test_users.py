import json
from fastapi import status
from tests.test_utils import assert_response_structure, create_user_data
from tests.conftest import global_fake_redis

class TestUser:
    def test_register_initiate_success(self, client):
        """Submit user details to trigger an OTP generation and save the pending user to Redis."""
        user_details = create_user_data()

        response = client.post("/users/register", json=user_details)
        assert response.status_code == status.HTTP_200_OK

        body = response.json()
        assert body["message"] == "OTP sent to your email. Valid for 10 minutes."
        assert global_fake_redis.exists(f"pending_user:{user_details['email']}")

    def test_verify_otp_and_register_success(self, client):
        """Retrieve the OTP from Redis and submit it to complete the user registration process."""
        user_details = create_user_data()
        email = user_details["email"]
        client.post("/users/register", json=user_details)

        # Peek into Redis to get the dynamic OTP
        raw_data = global_fake_redis.get(f"pending_user:{email}")
        otp = json.loads(raw_data)["otp"]

        response = client.post(f"/users/verify-otp?email={email}&otp={otp}")
        assert response.status_code == status.HTTP_200_OK

        body = response.json()
        assert_response_structure(body)
        assert body["message"] == "Email verified and user registered successfully."
        assert body["data"]["email"] == email

    def test_register_duplicate_email_error(self, client):
        """Try registering with an existing email to ensure the system blocks duplicates."""
        user_details = create_user_data(email="duplicate@gmail.com")
        client.post("/users/register", json=user_details)
        otp = json.loads(
            global_fake_redis.get(f"pending_user:{user_details['email']}")
        )["otp"]
        client.post(f"/users/verify-otp?email={user_details['email']}&otp={otp}")

        response = client.post("/users/register", json=user_details)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()["detail"] == "Email already registered"

    def test_login_success(self, client):
        """Authenticate with valid credentials after verifying email to receive access tokens."""
        user_details = create_user_data(email="login-user@gmail.com")
        email = user_details["email"]

        # Complete 2-step registration
        client.post("/users/register", json=user_details)
        otp = json.loads(global_fake_redis.get(f"pending_user:{email}"))["otp"]
        client.post(f"/users/verify-otp?email={email}&otp={otp}")

        # Attempt Login
        login_payload = {"email": email, "password": user_details["password"]}
        response = client.post("/users/login", json=login_payload)

        assert response.status_code == status.HTTP_200_OK
        body = response.json()
        assert_response_structure(body)
        assert "access_token" in body["data"]

    def test_refresh_token_success(self, client):
        """Swap a valid refresh token for a new pair to verify the rotation mechanism."""
        user_details = create_user_data(email="refresher@gmail.com")
        email = user_details["email"]

        # Register and Login
        client.post("/users/register", json=user_details)
        otp = json.loads(global_fake_redis.get(f"pending_user:{email}"))["otp"]
        client.post(f"/users/verify-otp?email={email}&otp={otp}")

        login_res = client.post(
            "/users/login", json={"email": email, "password": user_details["password"]}
        )
        refresh_token = login_res.json()["data"]["refresh_token"]

        # Refresh tokens
        response = client.post(f"/users/refresh?refresh_token={refresh_token}")
        assert response.status_code == status.HTTP_200_OK
        assert "access_token" in response.json()["data"]

    def test_refresh_token_reuse_failure(self, client):
        """Try using the same refresh token twice to confirm the blacklist prevents reuse."""
        user_details = create_user_data(email="reuser@gmail.com")
        email = user_details["email"]

        # Setup: Register and Login
        client.post("/users/register", json=user_details)
        otp = json.loads(global_fake_redis.get(f"pending_user:{email}"))["otp"]
        client.post(f"/users/verify-otp?email={email}&otp={otp}")

        login_res = client.post(
            "/users/login", json={"email": email, "password": user_details["password"]}
        )
        token = login_res.json()["data"]["refresh_token"]

        # First use succeeds
        client.post(f"/users/refresh?refresh_token={token}")

        # Second use must fail
        response = client.post(f"/users/refresh?refresh_token={token}")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json()["detail"] == "Token has already been used"
