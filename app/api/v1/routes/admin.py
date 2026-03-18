from fastapi import APIRouter, status, HTTPException, Query
from typing import Annotated
from app.api.v1.dependencies import DBDep, AdminDep, AdminRepoDep
from app.api.v1.schemas.response import create_response, ResponseSchema
from app.api.v1.schemas.item import (
    ItemOutSchema,
    ItemSchema,
    ItemUpdateSchema,
    ItemOutDetailedSchema,
)
from app.api.v1.schemas.user import UserOutSchema, UserUpdateSchema
from app.api.v1.schemas.pagination import PaginationSchema
from app.core.logger import log_func

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get(
    "/items",
    status_code=status.HTTP_200_OK,
    response_model=ResponseSchema,
)
@log_func
async def get_all_items(
    db: DBDep,
    admin_repo: AdminRepoDep,
    admin_dep: AdminDep,
    pagination: Annotated[PaginationSchema, Query()],
):
    """Get all items."""
    items = await admin_repo.get_all_items(
        db=db, page=pagination.page, size=pagination.size
    )
    items_data = [ItemOutSchema.model_validate(item).model_dump() for item in items]
    return create_response(items_data, "Successfully retrieved all items.")


@router.get(
    "/users",
    status_code=status.HTTP_200_OK,
    response_model=ResponseSchema,
)
@log_func
async def get_all_users(
    db: DBDep,
    admin_repo: AdminRepoDep,
    admin_dep: AdminDep,
    pagination: Annotated[PaginationSchema, Query()],
):
    """Get all users."""
    users = await admin_repo.get_all_users(
        db=db, page=pagination.page, size=pagination.size
    )
    users_data = [UserOutSchema.model_validate(user).model_dump() for user in users]
    return create_response(users_data, "Successfully retrieved all users.")


@router.get(
    "/items/detailed", status_code=status.HTTP_200_OK, response_model=ResponseSchema
)
@log_func
async def get_detailed_items(
    db: DBDep,
    admin_repo: AdminRepoDep,
    admin_dep: AdminDep,
    pagination: Annotated[PaginationSchema, Query()],
):
    """Get all items with user details."""
    items = await admin_repo.get_all_detailed_items(
        db=db, page=pagination.page, size=pagination.size
    )
    items_data = [
        ItemOutDetailedSchema.model_validate(item).model_dump() for item in items
    ]
    return create_response(
        items_data, "Successfully retrieved items with user details."
    )


@router.post(
    "/items",
    status_code=status.HTTP_201_CREATED,
    response_model=ResponseSchema,
)
@log_func
async def create_item(
    item: ItemSchema,
    db: DBDep,
    admin_dep: AdminDep,
    admin_repo: AdminRepoDep,
):
    """Create a new item and check it doesn't already exist."""
    if await admin_repo.get_item_by_title(item.title, admin_dep.id, db):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Item already exists"
        )
    new_item = await admin_repo.create_item(item, owner_id=admin_dep.id, db=db)
    item_data = ItemOutSchema.model_validate(new_item).model_dump()
    return create_response(item_data, "Item added successfully.")


@router.patch(
    "/items/{item_id}",
    status_code=status.HTTP_200_OK,
    response_model=ResponseSchema,
)
@log_func
async def update_item(
    item_id: int,
    item: ItemUpdateSchema,
    db: DBDep,
    admin_repo: AdminRepoDep,
    admin_dep: AdminDep,
):
    """Update specific fields of an item (Partial update)."""
    existing_item = await admin_repo.get_item_by_id(item_id, db)
    if not existing_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Item not found"
        )

    update_data = item.model_dump(exclude_unset=True)
    updated_item = await admin_repo.update_item(item_id, update_data, db)
    updated_item_data = ItemOutSchema.model_validate(updated_item).model_dump()

    return create_response(updated_item_data, "Item updated successfully.")


@router.patch(
    "/users/{user_id}",
    status_code=status.HTTP_200_OK,
    response_model=ResponseSchema,
)
@log_func
async def update_user(
    user_id: int,
    user: UserUpdateSchema,
    db: DBDep,
    admin_repo: AdminRepoDep,
    admin_dep: AdminDep,
):
    """Update specific fields of user (Partial Update)."""
    existing_user = await admin_repo.get_user_by_id(user_id, db)
    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    update_user = user.model_dump(exclude_unset=True)
    updated_user = await admin_repo.update_user(user_id, update_user, db)
    updated_user_data = UserOutSchema.model_validate(updated_user).model_dump()

    return create_response(updated_user_data, "User updated successfully.")


@router.delete(
    "/items/{item_id}",
    status_code=status.HTTP_200_OK,
    response_model=ResponseSchema,
)
@log_func
async def delete_item(
    item_id: int,
    db: DBDep,
    admin_repo: AdminRepoDep,
    admin_dep: AdminDep,
):
    """Delete an item if it exists."""
    item = await admin_repo.get_item_by_id(item_id, db)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Item not found"
        )
    deleted_item_data = ItemOutSchema.model_validate(item).model_dump()

    await admin_repo.delete_item(item_id, db)
    return create_response(deleted_item_data, "Item removed successfully.")
