import time
from fastapi import FastAPI, Request
from app.api.v1.api import api_router
from app.db.models.base import Base
from app.db.database import engine

app = FastAPI()

app.include_router(api_router)
Base.metadata.create_all(bind=engine)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = time.perf_counter() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


@app.get("/")
async def root():
    return {"message": "API is running"}
