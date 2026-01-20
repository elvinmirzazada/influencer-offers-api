from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.offer import Offer, Payout, CountryOverride, CustomPayout
from app.schemas.offer import OfferCreate, OfferUpdate


class OfferRepository:
    """Repository for Offer CRUD operations."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, offer_data: OfferCreate) -> Offer:
        """Create a new offer with payout."""
        # Convert categories list to comma-separated string
        categories_str = ",".join([cat.value for cat in offer_data.categories])

        # Create offer
        db_offer = Offer(
            title=offer_data.title,
            description=offer_data.description,
            categories=categories_str
        )
        self.db.add(db_offer)
        self.db.flush()

        # Create payout
        db_payout = Payout(
            offer_id=db_offer.id,
            payout_type=offer_data.payout.payout_type,
            cpa_amount=offer_data.payout.cpa_amount,
            fixed_amount=offer_data.payout.fixed_amount
        )
        self.db.add(db_payout)
        self.db.flush()

        # Create country overrides if any
        if offer_data.payout.country_overrides:
            for override in offer_data.payout.country_overrides:
                db_override = CountryOverride(
                    payout_id=db_payout.id,
                    country_code=override.country_code,
                    cpa_amount=override.cpa_amount
                )
                self.db.add(db_override)

        self.db.commit()
        self.db.refresh(db_offer)
        return db_offer

    def get_by_id(self, offer_id: int) -> Optional[Offer]:
        """Get offer by ID."""
        return self.db.query(Offer).filter(Offer.id == offer_id).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[Offer]:
        """Get all offers with pagination."""
        return self.db.query(Offer).offset(skip).limit(limit).all()

    def get_by_title(self, title: str, skip: int = 0, limit: int = 100) -> List[Offer]:
        """Search offers by title."""
        return self.db.query(Offer).filter(
            Offer.title.ilike(f"%{title}%")
        ).offset(skip).limit(limit).all()

    def count_all(self) -> int:
        """Count all offers."""
        return self.db.query(Offer).count()

    def count_by_title(self, title: str) -> int:
        """Count offers matching title search."""
        return self.db.query(Offer).filter(Offer.title.ilike(f"%{title}%")).count()

    def update(self, offer_id: int, offer_data: OfferUpdate) -> Optional[Offer]:
        """Update an offer."""
        db_offer = self.get_by_id(offer_id)
        if not db_offer:
            return None

        # Update offer fields
        if offer_data.title is not None:
            db_offer.title = offer_data.title
        if offer_data.description is not None:
            db_offer.description = offer_data.description
        if offer_data.categories is not None:
            db_offer.categories = ",".join([cat.value for cat in offer_data.categories])

        # Update payout if provided
        if offer_data.payout is not None:
            if db_offer.payout:
                if offer_data.payout.payout_type is not None:
                    db_offer.payout.payout_type = offer_data.payout.payout_type
                if offer_data.payout.cpa_amount is not None:
                    db_offer.payout.cpa_amount = offer_data.payout.cpa_amount
                if offer_data.payout.fixed_amount is not None:
                    db_offer.payout.fixed_amount = offer_data.payout.fixed_amount

                # Update country overrides if provided
                if offer_data.payout.country_overrides is not None:
                    # Delete existing overrides
                    for override in db_offer.payout.country_overrides:
                        self.db.delete(override)

                    # Add new overrides
                    for override in offer_data.payout.country_overrides:
                        db_override = CountryOverride(
                            payout_id=db_offer.payout.id,
                            country_code=override.country_code,
                            cpa_amount=override.cpa_amount
                        )
                        self.db.add(db_override)

        self.db.commit()
        self.db.refresh(db_offer)
        return db_offer

    def delete(self, offer_id: int) -> bool:
        """Delete an offer."""
        db_offer = self.get_by_id(offer_id)
        if not db_offer:
            return False

        self.db.delete(db_offer)
        self.db.commit()
        return True

    def get_custom_payout_for_influencer(self, offer_id: int, influencer_id: int) -> Optional[CustomPayout]:
        """Get custom payout for a specific influencer in an offer."""
        return self.db.query(CustomPayout).filter(
            CustomPayout.offer_id == offer_id,
            CustomPayout.influencer_id == influencer_id
        ).first()

    def create_custom_payout(self, offer_id: int, influencer_id: int,
                            payout_type: str, cpa_amount: Optional[float] = None,
                            fixed_amount: Optional[float] = None) -> CustomPayout:
        """Create a custom payout for an influencer."""
        db_custom_payout = CustomPayout(
            offer_id=offer_id,
            influencer_id=influencer_id,
            payout_type=payout_type,
            cpa_amount=cpa_amount,
            fixed_amount=fixed_amount
        )
        self.db.add(db_custom_payout)
        self.db.commit()
        self.db.refresh(db_custom_payout)
        return db_custom_payout

