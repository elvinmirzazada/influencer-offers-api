import logging
from typing import List, Optional
from sqlalchemy.orm import Session

from app.repositories.offer_repository import OfferRepository
from app.repositories.influencer_repository import InfluencerRepository
from app.schemas.offer import (
    OfferCreate, OfferUpdate, OfferResponse, OfferListResponse,
    InfluencerOfferResponse, InfluencerOfferListResponse, InfluencerOfferPayoutInfo
)
from app.models.offer import Offer, PayoutType, CategoryEnum

logger = logging.getLogger(__name__)


class OfferService:
    """Service for offer business logic."""

    def __init__(self, db: Session):
        self.db = db
        self.offer_repo = OfferRepository(db)
        self.influencer_repo = InfluencerRepository(db)

    def create_offer(self, offer_data: OfferCreate) -> OfferResponse:
        """Create a new offer."""
        logger.debug(f"Validating payout for new offer: {offer_data.title}")
        # Validate payout data based on type
        self._validate_payout(offer_data.payout.payout_type,
                            offer_data.payout.cpa_amount,
                            offer_data.payout.fixed_amount)

        logger.debug(f"Creating offer in database: {offer_data.title}")
        offer = self.offer_repo.create(offer_data)
        logger.info(f"Offer created in service: ID={offer.id}, Title={offer.title}")
        return self._convert_to_response(offer)

    def get_offer(self, offer_id: int) -> Optional[OfferResponse]:
        """Get offer by ID."""
        offer = self.offer_repo.get_by_id(offer_id)
        if not offer:
            return None
        return self._convert_to_response(offer)

    def list_offers(self, skip: int = 0, limit: int = 100) -> OfferListResponse:
        """List all offers."""
        offers = self.offer_repo.get_all(skip, limit)
        total = self.offer_repo.count_all()
        return OfferListResponse(
            offers=[self._convert_to_response(offer) for offer in offers],
            total=total
        )

    def search_offers_by_title(self, title: str, skip: int = 0, limit: int = 100) -> OfferListResponse:
        """Search offers by title."""
        offers = self.offer_repo.get_by_title(title, skip, limit)
        total = self.offer_repo.count_by_title(title)
        return OfferListResponse(
            offers=[self._convert_to_response(offer) for offer in offers],
            total=total
        )

    def update_offer(self, offer_id: int, offer_data: OfferUpdate) -> Optional[OfferResponse]:
        """Update an offer."""
        # Validate payout if being updated
        if offer_data.payout:
            # Get existing offer to determine payout type
            existing_offer = self.offer_repo.get_by_id(offer_id)
            if not existing_offer:
                return None

            payout_type = offer_data.payout.payout_type or existing_offer.payout.payout_type
            cpa_amount = offer_data.payout.cpa_amount if offer_data.payout.cpa_amount is not None else existing_offer.payout.cpa_amount
            fixed_amount = offer_data.payout.fixed_amount if offer_data.payout.fixed_amount is not None else existing_offer.payout.fixed_amount

            self._validate_payout(payout_type, cpa_amount, fixed_amount)

        offer = self.offer_repo.update(offer_id, offer_data)
        if not offer:
            return None
        return self._convert_to_response(offer)

    def delete_offer(self, offer_id: int) -> bool:
        """Delete an offer."""
        return self.offer_repo.delete(offer_id)

    def list_offers_for_influencer(self, influencer_id: int, title: Optional[str] = None,
                                   skip: int = 0, limit: int = 100) -> InfluencerOfferListResponse:
        """
        List offers from the perspective of a specific influencer.
        Custom payouts take precedence over base payouts.
        """
        logger.debug(f"Checking if influencer exists: {influencer_id}")
        # Verify influencer exists
        influencer = self.influencer_repo.get_by_id(influencer_id)
        if not influencer:
            logger.warning(f"Influencer not found: {influencer_id}")
            return InfluencerOfferListResponse(offers=[], total=0)

        logger.debug(f"Fetching offers for influencer {influencer_id}")
        # Get offers (with optional title filter)
        if title:
            offers = self.offer_repo.get_by_title(title, skip, limit)
            total = self.offer_repo.count_by_title(title)
        else:
            offers = self.offer_repo.get_all(skip, limit)
            total = self.offer_repo.count_all()

        logger.debug(f"Converting {len(offers)} offers to influencer-specific responses")
        # Convert to influencer-specific responses
        influencer_offers = []
        for offer in offers:
            influencer_offer = self._convert_to_influencer_response(offer, influencer_id)
            influencer_offers.append(influencer_offer)

        return InfluencerOfferListResponse(
            offers=influencer_offers,
            total=total
        )

    def _convert_to_response(self, offer: Offer) -> OfferResponse:
        """Convert Offer model to OfferResponse schema."""
        # Parse categories from comma-separated string
        categories = [CategoryEnum(cat) for cat in offer.categories.split(",")]

        return OfferResponse(
            id=offer.id,
            title=offer.title,
            description=offer.description,
            categories=categories,
            payout=offer.payout,
            created_at=offer.created_at,
            updated_at=offer.updated_at
        )

    def _convert_to_influencer_response(self, offer: Offer, influencer_id: int) -> InfluencerOfferResponse:
        """
        Convert Offer to InfluencerOfferResponse with custom payout logic.
        Custom payouts take precedence over base payouts.
        """
        # Parse categories
        categories = [CategoryEnum(cat) for cat in offer.categories.split(",")]

        # Check for custom payout
        custom_payout = self.offer_repo.get_custom_payout_for_influencer(offer.id, influencer_id)

        if custom_payout:
            # Custom payout exists - use it exclusively (no country overrides)
            payout_info = self._calculate_payout_info(
                custom_payout.payout_type,
                custom_payout.cpa_amount,
                custom_payout.fixed_amount,
                []  # No country overrides for custom payouts
            )
        else:
            # Use base payout with country overrides
            payout_info = self._calculate_payout_info(
                offer.payout.payout_type,
                offer.payout.cpa_amount,
                offer.payout.fixed_amount,
                offer.payout.country_overrides
            )

        return InfluencerOfferResponse(
            id=offer.id,
            title=offer.title,
            description=offer.description,
            categories=categories,
            payout_info=payout_info,
            created_at=offer.created_at,
            updated_at=offer.updated_at
        )

    def _calculate_payout_info(self, payout_type: PayoutType, cpa_amount: Optional[float],
                               fixed_amount: Optional[float], country_overrides: list) -> InfluencerOfferPayoutInfo:
        """
        Calculate payout display information based on type and country overrides.
        """
        if payout_type == PayoutType.FIXED:
            return InfluencerOfferPayoutInfo(
                payout_type="Fixed",
                display_text=f"${fixed_amount:.2f} Fixed",
                min_amount=fixed_amount,
                max_amount=fixed_amount
            )

        elif payout_type == PayoutType.CPA:
            if country_overrides:
                # Find min and max CPA amounts
                amounts = [cpa_amount] + [override.cpa_amount for override in country_overrides]
                min_amount = min(amounts)
                max_amount = max(amounts)

                if min_amount == max_amount:
                    display_text = f"${min_amount:.2f} CPA"
                else:
                    display_text = f"${min_amount:.2f} - ${max_amount:.2f} CPA"

                return InfluencerOfferPayoutInfo(
                    payout_type="CPA",
                    display_text=display_text,
                    min_amount=min_amount,
                    max_amount=max_amount
                )
            else:
                return InfluencerOfferPayoutInfo(
                    payout_type="CPA",
                    display_text=f"${cpa_amount:.2f} CPA",
                    min_amount=cpa_amount,
                    max_amount=cpa_amount
                )

        elif payout_type == PayoutType.CPA_FIXED:
            if country_overrides:
                # Find min and max CPA amounts
                cpa_amounts = [cpa_amount] + [override.cpa_amount for override in country_overrides]
                min_cpa = min(cpa_amounts)
                max_cpa = max(cpa_amounts)

                if min_cpa == max_cpa:
                    display_text = f"${min_cpa:.2f} CPA + ${fixed_amount:.2f} Fixed"
                else:
                    display_text = f"${min_cpa:.2f} - ${max_cpa:.2f} CPA + ${fixed_amount:.2f} Fixed"

                return InfluencerOfferPayoutInfo(
                    payout_type="CPA + Fixed",
                    display_text=display_text,
                    min_amount=min_cpa + fixed_amount,
                    max_amount=max_cpa + fixed_amount
                )
            else:
                total_amount = cpa_amount + fixed_amount
                return InfluencerOfferPayoutInfo(
                    payout_type="CPA + Fixed",
                    display_text=f"${cpa_amount:.2f} CPA + ${fixed_amount:.2f} Fixed",
                    min_amount=total_amount,
                    max_amount=total_amount
                )
        else:
            raise ValueError("Invalid payout type")

    def _validate_payout(self, payout_type: PayoutType, cpa_amount: Optional[float],
                        fixed_amount: Optional[float]) -> None:
        """Validate payout based on type."""
        if payout_type == PayoutType.CPA:
            if cpa_amount is None or cpa_amount <= 0:
                raise ValueError("CPA payout requires a valid cpa_amount")
            if fixed_amount is not None:
                raise ValueError("CPA payout should not have fixed_amount")

        elif payout_type == PayoutType.FIXED:
            if fixed_amount is None or fixed_amount <= 0:
                raise ValueError("Fixed payout requires a valid fixed_amount")
            if cpa_amount is not None:
                raise ValueError("Fixed payout should not have cpa_amount")

        elif payout_type == PayoutType.CPA_FIXED:
            if cpa_amount is None or cpa_amount <= 0:
                raise ValueError("CPA+Fixed payout requires a valid cpa_amount")
            if fixed_amount is None or fixed_amount <= 0:
                raise ValueError("CPA+Fixed payout requires a valid fixed_amount")

