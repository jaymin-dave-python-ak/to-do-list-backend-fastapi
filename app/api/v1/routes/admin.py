from fastapi import APIRouter, status
from app.api.v1.dependencies import db_dep, admin_dep, admin_repo_dep
from app.api.v1.schemas.response import create_response, ResponseSchema
from app.api.v1.schemas.item import ItemOutSchema
from app.api.v1.schemas.user import UserOutSchema
from app.core.logger import log_func

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/items", status_code=status.HTTP_200_OK, response_model=ResponseSchema)
@log_func
def get_all_items(db: db_dep, admin_repo: admin_repo_dep, admin_dep: admin_dep):
    """Get all items."""
    items = admin_repo.get_all_items(db)
    items_data = [ItemOutSchema.model_validate(item).model_dump() for item in items]
    return create_response(items_data, "Successfully retrieved all items.")


@router.get("/users", status_code=status.HTTP_200_OK, response_model=ResponseSchema)
@log_func
def get_all_users(db: db_dep, admin_repo: admin_repo_dep, admin_dep: admin_dep):
    """Get all users."""
    users = admin_repo.get_all_users(db)
    users_data = [UserOutSchema.model_validate(user).model_dump() for user in users]
    return create_response(users_data, "Successfully retrieved all users.")
