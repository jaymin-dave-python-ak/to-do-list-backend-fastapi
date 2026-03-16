# from fastapi import status
# from tests.test_utils import assert_response_structure, create_user_data

# class TestUser:
#     def test_register_user_success(self, client):
#         """Test successful user registration."""
#         user_details = create_user_data()
        
#         response = client.post("/users/register", json=user_details)
#         assert response.status_code == status.HTTP_201_CREATED
        
#         body = response.json()
#         assert_response_structure(body)
        
#         assert body["message"] == "User registered successfully."
#         assert body["data"]["email"] == user_details["email"]

#     def test_register_duplicate_email_error(self, client):
#         """Test registration with an existing email."""
#         user_details = create_user_data(email="duplicate@gmail.com")
        
#         client.post("/users/register", json=user_details)
        
#         response = client.post("/users/register", json=user_details)
#         assert response.status_code == status.HTTP_400_BAD_REQUEST
        
#         body = response.json()
#         assert body["detail"] == "Email already registered"

#     def test_login_success(self, client):
#         """Test successful user login."""
#         user_details = create_user_data(email="login-user@gmail.com")
#         login_payload = {"email": user_details["email"], "password": user_details["password"]}
        
#         client.post("/users/register", json=user_details)
        
#         response = client.post("/users/login", json=login_payload)
#         assert response.status_code == status.HTTP_200_OK
        
#         body = response.json()
#         assert_response_structure(body)
        
#         assert body["message"] == "Login successful."
#         assert "access_token" in body["data"]

#     def test_login_non_existent_user_error(self, client):
#         """Test login failure for a user that does not exist."""
#         login_payload = {"email": "not_existent@gmail.com", "password": "somepassword"}
        
#         response = client.post("/users/login", json=login_payload)
#         assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
#         body = response.json()
#         assert body["detail"] == "Invalid credentials"

#     def test_refresh_token_success(self, client):
#         """Test successful token rotation using a valid refresh token."""
#         user_details = create_user_data(email="refresher@gmail.com")
#         client.post("/users/register", json=user_details)
        
#         login_payload = {"email": user_details["email"], "password": user_details["password"]}
#         login_response = client.post("/users/login", json=login_payload)
        
#         refresh_token = login_response.json()["data"]["refresh_token"]
        
#         response = client.post(f"/users/refresh?refresh_token={refresh_token}")
        
#         assert response.status_code == status.HTTP_200_OK
        
#         body = response.json()
#         assert_response_structure(body)
        
#         assert body["message"] == "Tokens rotated successfully."
#         assert "access_token" in body["data"]
#         assert "refresh_token" in body["data"]

#     def test_refresh_token_invalid_error(self, client):
#         """Test refresh failure with an invalid token string."""
#         invalid_token = "not.a.real.jwt.token"
        
#         response = client.post(f"/users/refresh?refresh_token={invalid_token}")
        
#         assert response.status_code == status.HTTP_401_UNAUTHORIZED
#         assert response.json()["detail"] == "Invalid or expired refresh token"

#     def test_refresh_token_reuse_failure(self, client):
#         """Test that a refresh token cannot be used twice (Blacklist check)."""
#         user_details = create_user_data(email="reuser@gmail.com")
#         client.post("/users/register", json=user_details)
        
#         login_payload = {"email": user_details["email"], "password": user_details["password"]}
#         login_response = client.post("/users/login", json=login_payload)
#         refresh_token = login_response.json()["data"]["refresh_token"]

#         first_refresh = client.post(f"/users/refresh?refresh_token={refresh_token}")
#         assert first_refresh.status_code == status.HTTP_200_OK

#         second_refresh = client.post(f"/users/refresh?refresh_token={refresh_token}")
        
#         assert second_refresh.status_code == status.HTTP_401_UNAUTHORIZED
#         assert second_refresh.json()["detail"] == "Token has already been used"