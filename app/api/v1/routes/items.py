from fastapi import APIRouter, status, HTTPException, Depends
from typing import Annotated
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models.user import UserModel
from app.repositories.item_repo import ItemRepository
from app.api.v1.dependencies import get_current_user
from app.api.v1.schemas.response import ResponseSchema, create_response
from app.api.v1.schemas.item import ItemOutSchema, ItemSchema

router = APIRouter(
    prefix="/items", tags=["Items"], dependencies=[Depends(get_current_user)]
)
ItemRepo = ItemRepository()
DBDep = Annotated[Session, Depends(get_db)]
UserDep = Annotated[UserModel, Depends(get_current_user)]


# Get All Items
@router.get("/", status_code=status.HTTP_200_OK, response_model=ResponseSchema)
def get_items(db: DBDep, current_user: UserDep):
    """Retrieve all items of current user."""
    items = ItemRepo.get_all(current_user.id, db)
    return create_response(items, "Successfully retrieved all items.")


# Create an Item
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=ResponseSchema)
def create_item(db: DBDep, current_user: UserDep, item: ItemSchema):
    """Create a new item and check it doesn't already exist."""
    if ItemRepo.get_by_title(item.title, db):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Item already exists"
        )
    new_item = ItemRepo.create(item, owner_id=current_user.id, db=db)
    item_data = ItemOutSchema.model_validate(new_item).model_dump()
    return create_response(item_data, "Item added successfully.")


# FROM HERE ...
@router.put("/{item_id}", status_code=status.HTTP_200_OK)
async def replace_item(item_id: int, item: ItemSchema, db: DBDep):
    """Replace an entire item (Full update)."""
    updated_item = ItemRepo.replace(item_id, item.model_dump(), db)
    if not updated_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Item {item_id} not found"
        )
    return {"message": f"Item {item_id} fully updated", "data": updated_item}


@router.patch("/{item_id}", status_code=status.HTTP_200_OK)
async def update_item(item_id: int, item: ItemSchema, db: DBDep):
    """Update specific fields of an item (Partial update)."""
    # exclude_unset=True ensures we only update fields sent by the client
    update_data = item.model_dump(exclude_unset=True)
    updated_item = ItemRepo.update(item_id, update_data, db)
    if not updated_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Item {item_id} not found"
        )
    return {"message": f"Item {item_id} partially updated", "data": updated_item}


@router.delete("/{item_id}", status_code=status.HTTP_200_OK)
async def delete_item(
    item_id: int, db: DBDep, current_user: UserModel = Depends(get_current_user)
):
    if not current_user.is_active:
        raise HTTPException(status_code=403, detail="Inactive user")

    item = ItemRepo.get_by_id(item_id, db)
    if item.owner_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to delete this item"
        )

    if not ItemRepo.delete(item_id, db):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Item {item_id} not found"
        )
    return {"message": f"Item {item_id} removed successfully"}
