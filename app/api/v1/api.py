from fastapi import APIRouter
from app.api.v1.routes import items
from app.api.v1.routes import users
from app.api.v1.routes import admin

api_router = APIRouter()
api_router.include_router(items.router)
api_router.include_router(users.router)
api_router.include_router(admin.router)
