from app.api.v1.schemas.item import ItemStatus, DeactivationType

def assert_response_structure(body: dict, success: bool = True):
    assert "success" in body
    assert "message" in body
    assert "data" in body
    assert body["success"] is success


def create_user_data(
    email="test-user@gmail.com", username="test-user", password="test-user123"
):
    """Generates a dictionary for user registration/login tests."""
    return {
        "email": email,
        "username": username,
        "is_active": True,
        "is_admin": False,
        "password": password,
    }

def create_admin_data(
    email="test-admin@gmail.com", username="test-admin", password="test-admin123"
):
    """Generates a dictionary for admin registration tests."""
    return {
        "email": email,
        "username": username,
        "is_active": True,
        "is_admin": True,
        "password": password,
    }

def create_item_data(title="item title", desc="item description"):
    """Generates a dictionary for item creation tests with new status logic."""
    return {
        "title": title,
        "desc": desc,
        "status": ItemStatus.pending.value,  
        "remind_me_at": None,               
    }


def update_item_data(title="updated title", status=ItemStatus.running.value):
    """Generates a dictionary for item update tests."""
    return {
        "title": title,
        "status": status
    }

def deactivate_item_data(manual=True):
    """Specific helper to test deactivation logic."""
    return {
        "status": ItemStatus.deactivated.value
    }
