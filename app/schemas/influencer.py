from pydantic import BaseModel, EmailStr, Field, ConfigDict

from app.schemas.base import TimestampSchema


class InfluencerBase(BaseModel):
    """Base schema for influencer."""
    name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr


class InfluencerCreate(InfluencerBase):
    """Schema for creating an influencer."""
    pass


class InfluencerUpdate(BaseModel):
    """Schema for updating an influencer."""
    name: str = Field(None, min_length=1, max_length=255)
    email: EmailStr = None


class InfluencerResponse(InfluencerBase, TimestampSchema):
    """Schema for influencer response."""
    model_config = ConfigDict(from_attributes=True)

    id: int

