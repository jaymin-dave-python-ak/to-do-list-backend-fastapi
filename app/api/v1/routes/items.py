from fastapi import APIRouter, status, HTTPException, Depends
from typing import Annotated
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.repositories.item_repo import ItemRepository
from app.api.v1.schemas.item import ItemSchema

router = APIRouter(prefix="/items", tags=["Items"])
repo = ItemRepository()

DBDep = Annotated[Session, Depends(get_db)]


@router.get("/", status_code=status.HTTP_200_OK)
async def get_items(db: DBDep):
    """Retrieve all items from the database."""
    items = repo.get_all(db)
    return {"message": "Welcome to the to-do-list", "data": items}


@router.get("/{item_id}", status_code=status.HTTP_200_OK)
async def get_one_item(item_id: int, db: DBDep):
    """Retrieve a single item by its ID."""
    item = repo.get_by_id(item_id, db)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Item {item_id} not found"
        )
    return {"message": f"Found item {item_id}", "data": item}


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_item(item: ItemSchema, db: DBDep):
    """Create a new item and ensure it doesn't already exist."""
    if repo.get_by_title(item.title, db):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Item already exists"
        )
    return repo.create(item, db)


@router.put("/{item_id}", status_code=status.HTTP_200_OK)
async def replace_item(item_id: int, item: ItemSchema, db: DBDep):
    """Replace an entire item (Full update)."""
    # Use model_dump() to pass the data as a dictionary to the repo
    updated_item = repo.replace(item_id, item.model_dump(), db)
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
    updated_item = repo.update(item_id, update_data, db)
    if not updated_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Item {item_id} not found"
        )
    return {"message": f"Item {item_id} partially updated", "data": updated_item}


@router.delete("/{item_id}", status_code=status.HTTP_200_OK)
async def delete_item(item_id: int, db: DBDep):
    """Delete an item by ID."""
    if not repo.delete(item_id, db):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Item {item_id} not found"
        )
    return {"message": f"Item {item_id} removed successfully"}
