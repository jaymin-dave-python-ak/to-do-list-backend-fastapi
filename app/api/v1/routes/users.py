from fastapi import APIRouter, status, HTTPException, Depends
from typing import Annotated
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.repositories.users_repo import UserRepository
