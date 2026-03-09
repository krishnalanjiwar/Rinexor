from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional
import uuid

class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

class IDSchema(BaseSchema):
    id: str
    
class TimestampSchema(BaseSchema):
    created_at: datetime
    updated_at: Optional[datetime] = None

class PaginationParams(BaseSchema):
    page: int = 1
    page_size: int = 20
    sort_by: str = "created_at"
    sort_order: str = "desc"
    
class PaginatedResponse(BaseSchema):
    items: list
    total: int
    page: int
    page_size: int
    total_pages: int