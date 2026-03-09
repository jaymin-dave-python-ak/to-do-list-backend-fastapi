from fastapi import APIRouter, status, HTTPException
from app.api.v1.dependencies import db_dep, admin_dep, admin_repo_dep
from app.api.v1.schemas.response import create_response, ResponseSchema
from app.api.v1.schemas.item import ItemOutSchema, ItemSchema, ItemUpdateSchema
from app.api.v1.schemas.user import UserOutSchema, UserUpdateSchema
from app.core.logger import log_func

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get(
    "/items",
    status_code=status.HTTP_200_OK,
    response_model=ResponseSchema,
)
@log_func
def get_all_items(
    db: db_dep,
    admin_repo: admin_repo_dep,
    admin_dep: admin_dep,
):
    """Get all items."""
    items = admin_repo.get_all_items(db)
    items_data = [ItemOutSchema.model_validate(item).model_dump() for item in items]
    return create_response(items_data, "Successfully retrieved all items.")


@router.get(
    "/users",
    status_code=status.HTTP_200_OK,
    response_model=ResponseSchema,
)
@log_func
def get_all_users(
    db: db_dep,
    admin_repo: admin_repo_dep,
    admin_dep: admin_dep,
):
    """Get all users."""
    users = admin_repo.get_all_users(db)
    users_data = [UserOutSchema.model_validate(user).model_dump() for user in users]
    return create_response(users_data, "Successfully retrieved all users.")


@router.post(
    "/items",
    status_code=status.HTTP_201_CREATED,
    response_model=ResponseSchema,
)
@log_func
def create_item(
    item: ItemSchema,
    db: db_dep,
    admin_dep: admin_dep,
    admin_repo: admin_repo_dep,
):
    """Create a new item and check it doesn't already exist."""
    if admin_repo.get_item_by_title(item.title, admin_dep.id, db):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Item already exists"
        )
    new_item = admin_repo.create_item(item, owner_id=admin_dep.id, db=db)
    item_data = ItemOutSchema.model_validate(new_item).model_dump()
    return create_response(item_data, "Item added successfully.")


@router.patch(
    "/items/{item_id}",
    status_code=status.HTTP_200_OK,
    response_model=ResponseSchema,
)
@log_func
def update_item(
    item_id: int,
    item: ItemUpdateSchema,
    db: db_dep,
    admin_repo: admin_repo_dep,
    admin_dep: admin_dep,
):
    """Update specific fields of an item (Partial update)."""
    existing_item = admin_repo.get_item_by_id(item_id, db)
    if not existing_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Item not found"
        )

    update_data = item.model_dump(exclude_unset=True)
    updated_item = admin_repo.update_item(item_id, update_data, db)
    updated_item_data = ItemOutSchema.model_validate(updated_item).model_dump()

    return create_response(updated_item_data, "Item updated successfully.")


@router.patch(
    "/users/{user_id}",
    status_code=status.HTTP_200_OK,
    response_model=ResponseSchema,
)
@log_func
def update_user(
    user_id: int,
    user: UserUpdateSchema,
    db: db_dep,
    admin_repo: admin_repo_dep,
    admin_dep: admin_dep,
):
    """Update specific fields of user (Partial Update)."""
    existing_user = admin_repo.get_user_by_id(user_id, db)
    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    update_user = user.model_dump(exclude_unset=True)
    updated_user = admin_repo.update_user(user_id, update_user, db)
    updated_user_data = UserOutSchema.model_validate(updated_user).model_dump()

    return create_response(updated_user_data, "User updated successfully.")


@router.delete(
    "/items/{item_id}",
    status_code=status.HTTP_200_OK,
    response_model=ResponseSchema,
)
@log_func
def delete_item(
    item_id: int,
    db: db_dep,
    admin_repo: admin_repo_dep,
    admin_dep: admin_dep,
):
    """Delete an item if it exists."""
    item = admin_repo.get_item_by_id(item_id, db)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Item not found"
        )
    deleted_item_data = ItemOutSchema.model_validate(item).model_dump()

    admin_repo.delete_item(item_id, db)
    return create_response(deleted_item_data, "Item removed successfully.")
