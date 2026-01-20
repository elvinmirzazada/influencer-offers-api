from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Table, Enum as SQLEnum, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.core.database import Base


class CategoryEnum(str, enum.Enum):
    """Available offer categories."""
    GAMING = "Gaming"
    TECH = "Tech"
    HEALTH = "Health"
    NUTRITION = "Nutrition"
    FASHION = "Fashion"
    FINANCE = "Finance"


class PayoutType(str, enum.Enum):
    """Types of payouts."""
    CPA = "CPA"
    FIXED = "FIXED"
    CPA_FIXED = "CPA_FIXED"


# Association table for many-to-many relationship between offers and categories
offer_categories = Table(
    'offer_categories',
    Base.metadata,
    Column('offer_id', Integer, ForeignKey('offers.id', ondelete='CASCADE'), primary_key=True),
    Column('category', SQLEnum(CategoryEnum), primary_key=True)
)


class Offer(Base):
    """Offer model."""
    __tablename__ = "offers"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, index=True)
    description = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    categories = Column(String, nullable=False)  # Store as comma-separated values for simplicity
    payout = relationship("Payout", back_populates="offer", uselist=False, cascade="all, delete-orphan")
    custom_payouts = relationship("CustomPayout", back_populates="offer", cascade="all, delete-orphan")


class Payout(Base):
    """Base payout configuration for an offer."""
    __tablename__ = "payouts"

    id = Column(Integer, primary_key=True, index=True)
    offer_id = Column(Integer, ForeignKey('offers.id', ondelete='CASCADE'), nullable=False, unique=True)

    payout_type = Column(SQLEnum(PayoutType), nullable=False)

    # CPA configuration
    cpa_amount = Column(Float, nullable=True)  # Base CPA amount

    # Fixed configuration
    fixed_amount = Column(Float, nullable=True)  # Fixed amount

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    offer = relationship("Offer", back_populates="payout")
    country_overrides = relationship("CountryOverride", back_populates="payout", cascade="all, delete-orphan")


class CountryOverride(Base):
    """Country-specific CPA overrides."""
    __tablename__ = "country_overrides"

    id = Column(Integer, primary_key=True, index=True)
    payout_id = Column(Integer, ForeignKey('payouts.id', ondelete='CASCADE'), nullable=False)
    country_code = Column(String(2), nullable=False)  # ISO country code (e.g., 'DE', 'US')
    cpa_amount = Column(Float, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationship
    payout = relationship("Payout", back_populates="country_overrides")


class CustomPayout(Base):
    """Custom payout for specific influencer in an offer."""
    __tablename__ = "custom_payouts"

    id = Column(Integer, primary_key=True, index=True)
    offer_id = Column(Integer, ForeignKey('offers.id', ondelete='CASCADE'), nullable=False)
    influencer_id = Column(Integer, ForeignKey('influencers.id', ondelete='CASCADE'), nullable=False)

    payout_type = Column(SQLEnum(PayoutType), nullable=False)

    # CPA configuration
    cpa_amount = Column(Float, nullable=True)

    # Fixed configuration
    fixed_amount = Column(Float, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    offer = relationship("Offer", back_populates="custom_payouts")
    influencer = relationship("Influencer", back_populates="custom_payouts")

