from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict
from datetime import datetime

from app.models.offer import PayoutType
from app.schemas.base import TimestampSchema


class CountryOverrideBase(BaseModel):
    """Base schema for country override."""
    country_code: str = Field(..., min_length=2, max_length=2, description="ISO country code (e.g., 'DE', 'US')")
    cpa_amount: float = Field(..., gt=0, description="CPA amount for this country")


class CountryOverrideCreate(CountryOverrideBase):
    """Schema for creating a country override."""
    pass


class CountryOverrideResponse(CountryOverrideBase):
    """Schema for country override response."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime


class PayoutBase(BaseModel):
    """Base schema for payout."""
    payout_type: PayoutType
    cpa_amount: Optional[float] = Field(None, gt=0, description="CPA amount (required for CPA and CPA_FIXED types)")
    fixed_amount: Optional[float] = Field(None, gt=0, description="Fixed amount (required for FIXED and CPA_FIXED types)")


class PayoutCreate(PayoutBase):
    """Schema for creating a payout."""
    country_overrides: Optional[list[CountryOverrideCreate]] = Field(default_factory=list, description="Country-specific CPA overrides")


class PayoutUpdate(BaseModel):
    """Schema for updating a payout."""
    payout_type: Optional[PayoutType] = None
    cpa_amount: Optional[float] = Field(None, gt=0)
    fixed_amount: Optional[float] = Field(None, gt=0)
    country_overrides: Optional[list[CountryOverrideCreate]] = None


class PayoutResponse(PayoutBase, TimestampSchema):
    """Schema for payout response."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    country_overrides: list[CountryOverrideResponse] = []


class CustomPayoutBase(BaseModel):
    """Base schema for custom payout."""
    influencer_id: int
    payout_type: PayoutType
    cpa_amount: Optional[float] = Field(None, gt=0)
    fixed_amount: Optional[float] = Field(None, gt=0)


class CustomPayoutCreate(CustomPayoutBase):
    """Schema for creating a custom payout."""
    pass


class CustomPayoutResponse(CustomPayoutBase, TimestampSchema):
    """Schema for custom payout response."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    offer_id: int

