from fastapi import APIRouter, status, HTTPException
from app.api.v1.dependencies import db_dep, item_repo_dep, current_user_dep
from app.api.v1.schemas.response import ResponseSchema, create_response
from app.api.v1.schemas.item import ItemOutSchema, ItemSchema
from app.core.logger import log_func

router = APIRouter(prefix="/items", tags=["Items"])


@router.get("/", status_code=status.HTTP_200_OK, response_model=ResponseSchema)
@log_func
def get_items(db: db_dep, current_user: current_user_dep, item_repo: item_repo_dep):
    """Get all the items of current user."""
    items = item_repo.get_all(current_user.id, db)
    items_data = [ItemOutSchema.model_validate(item).model_dump() for item in items]
    return create_response(items_data, "Successfully retrieved all items.")


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=ResponseSchema)
@log_func
def create_item(
    item: ItemSchema,
    db: db_dep,
    current_user: current_user_dep,
    item_repo: item_repo_dep,
):
    """Create a new item and check it doesn't already exist."""
    if item_repo.get_by_title(item.title, current_user.id, db):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Item already exists"
        )
    new_item = item_repo.create(item, owner_id=current_user.id, db=db)
    item_data = ItemOutSchema.model_validate(new_item).model_dump()
    return create_response(item_data, "Item added successfully.")


@router.patch(
    "/{item_id}", status_code=status.HTTP_200_OK, response_model=ResponseSchema
)
@log_func
def update_item(
    item_id: int,
    item: ItemSchema,
    db: db_dep,
    item_repo: item_repo_dep,
    current_user: current_user_dep,
):
    """Update specific fields of an item (Partial update)."""
    existing_item = item_repo.get_by_id(item_id, db)
    if not existing_item:
        raise HTTPException(status_code=404, detail="Item not found")
    if existing_item.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to edit this item")

    update_data = item.model_dump(exclude_unset=True)
    updated_item = item_repo.update(item_id, update_data, db)
    updated_item_data = ItemOutSchema.model_validate(updated_item).model_dump()

    return create_response(updated_item_data, "Item updated successfully.")


@router.delete(
    "/{item_id}", status_code=status.HTTP_200_OK, response_model=ResponseSchema
)
@log_func
def delete_item(
    item_id: int, db: db_dep, item_repo: item_repo_dep, current_user: current_user_dep
):
    """Delete an item if it exists."""
    item = item_repo.get_by_id(item_id, db)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if item.owner_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to delete this item"
        )
    deleted_item_data = ItemOutSchema.model_validate(item).model_dump()

    item_repo.delete(item_id, db)
    return create_response(deleted_item_data, "Item removed successfully.")
