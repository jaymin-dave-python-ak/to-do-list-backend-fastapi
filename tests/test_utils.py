def assert_response_structure(body: dict, success: bool = True):
    assert "success" in body
    assert "message" in body
    assert "data" in body
    assert body["success"] is success


def create_user_data(
    email="jaymin4724@gmail.com", username="test-user", password="test-user123"
):
    """Generates a dictionary for user registration/login tests."""
    return {
        "email": email,
        "username": username,
        "is_active": True,
        "is_admin": False,
        "password": password,
    }


def create_item_data(title="item title", desc="item description"):
    """Generates a dictionary for item creation tests."""
    return {
        "title": title,
        "desc": desc,
    }


def update_item_data(title="item title x"):
    """Generates a dictionary for item updation tests."""
    return {
        "title": title,
    }

def generate_fixed_otp():
    return "123456"