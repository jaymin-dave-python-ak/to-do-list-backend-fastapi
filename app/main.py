from fastapi import FastAPI
from app.api.v1.api import api_router
from app.db.models.base import Base
from app.db.database import engine
from app.middleware.logging_middleware import log_requests_middelware

app = FastAPI()

app.middleware("http")(log_requests_middelware)

app.include_router(api_router)
Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return {"message": "API is running"}
