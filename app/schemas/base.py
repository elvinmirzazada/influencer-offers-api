from pydantic import BaseModel
from datetime import datetime


class TimestampSchema(BaseModel):
    """Base schema with timestamp fields."""
    created_at: datetime
    updated_at: datetime
