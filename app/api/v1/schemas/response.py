from typing import Any, Generic, TypeVar, Optional
from pydantic import BaseModel

T = TypeVar("T")


class ResponseSchema(BaseModel, Generic[T]):
    success: bool
    message: str
    data: Optional[T] = None


def create_response(
    data: Any = None, message: str = "Success", success: bool = True
) -> ResponseSchema:
    # Returning the model instance ensures validation
    return ResponseSchema(success=success, message=message, data=data)
