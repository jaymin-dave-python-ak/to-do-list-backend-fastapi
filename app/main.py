from fastapi import FastAPI, status
from app.api.v1.api import api_router
from app.db.models.base import Base
from app.db.database import engine
from app.middleware.logging_middleware import log_requests_middleware
from app.api.v1.schemas.response import ResponseSchema, create_response

app = FastAPI()

app.middleware("http")(log_requests_middleware)

app.include_router(api_router)
Base.metadata.create_all(bind=engine)


@app.get("/", status_code=status.HTTP_200_OK, response_model=ResponseSchema)
def root():
    return create_response([], "Server is running!")
