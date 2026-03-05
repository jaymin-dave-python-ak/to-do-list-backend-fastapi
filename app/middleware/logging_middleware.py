import time
import uuid
from fastapi import Request
from app.core.logger import logger


async def log_requests_middelware(request: Request, call_next):
    request_id = str(uuid.uuid4())
    start_time = time.perf_counter()

    # Pre-processing log
    logger.info(
        f"\n**********************************************************\n"
        f"ID: {request_id} | Method: {request.method} | Path: {request.url.path}"
    )

    response = await call_next(request)

    # Calculate duration
    process_time = time.perf_counter() - start_time

    # Post-processing log
    logger.info(
        f"ID: {request_id} | Path: {request.url.path} | "
        f"Status: {response.status_code} | Time: {process_time:.4f}s"
        f"\n**********************************************************\n"
    )

    # Add headers to response
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time"] = f"{process_time:.4f}s"

    return response
