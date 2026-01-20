from pydantic import BaseModel, Field, ConfigDict
from typing import Optional

from app.models.offer import CategoryEnum
from app.schemas.payout import PayoutCreate, PayoutUpdate, PayoutResponse
from app.schemas.base import TimestampSchema


class OfferBase(BaseModel):
    """Base schema for offer."""
    title: str = Field(..., min_length=1, max_length=255, description="Offer title")
    description: str = Field(..., min_length=1, description="Offer description")
    categories: list[CategoryEnum] = Field(..., min_length=1, description="Offer categories")


class OfferCreate(OfferBase):
    """Schema for creating an offer."""
    payout: PayoutCreate


class OfferUpdate(BaseModel):
    """Schema for updating an offer."""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, min_length=1)
    categories: Optional[list[CategoryEnum]] = Field(None, min_length=1)
    payout: Optional[PayoutUpdate] = None


class OfferResponse(OfferBase, TimestampSchema):
    """Schema for offer response."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    payout: PayoutResponse


class OfferListResponse(BaseModel):
    """Schema for listing offers."""
    offers: list[OfferResponse]
    total: int


class InfluencerOfferPayoutInfo(BaseModel):
    """Schema for payout information as seen by an influencer."""
    payout_type: str
    display_text: str  # e.g., "$20 - $30 CPA", "$1000 Fixed", "$20 CPA + $500 Fixed"
    min_amount: Optional[float] = None
    max_amount: Optional[float] = None


class InfluencerOfferResponse(TimestampSchema):
    """Schema for offer as seen by a specific influencer."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str
    categories: list[CategoryEnum]
    payout_info: InfluencerOfferPayoutInfo



class InfluencerOfferListResponse(BaseModel):
    """Schema for listing offers from influencer's perspective."""
    offers: list[InfluencerOfferResponse]
    total: int
