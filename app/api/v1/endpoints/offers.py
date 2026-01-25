import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.offer_service import OfferService
from app.schemas.offer import (
    OfferCreate, OfferUpdate, OfferResponse, OfferListResponse,
    InfluencerOfferListResponse
)

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/", response_model=OfferResponse, status_code=201)
def create_offer(
    offer_data: OfferCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new offer.

    - **title**: Name of the offer
    - **description**: Short description about the offer
    - **categories**: List of categories (Gaming, Tech, Health, Nutrition, Fashion, Finance)
    - **payout**: Payout configuration (CPA, Fixed, or CPA+Fixed)
    """
    logger.info(f"Creating new offer: {offer_data.title}")
    try:
        service = OfferService(db)
        offer = service.create_offer(offer_data)
        logger.info(f"Offer created successfully with ID: {offer.id}")
        return offer
    except ValueError as e:
        logger.warning(f"Validation error creating offer: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating offer: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/{offer_id}", response_model=OfferResponse)
def get_offer(
    offer_id: int,
    db: Session = Depends(get_db)
):
    """
    Get an offer by ID.
    """
    logger.info(f"Fetching offer with ID: {offer_id}")
    service = OfferService(db)
    offer = service.get_offer(offer_id)
    if not offer:
        logger.warning(f"Offer not found: {offer_id}")
        raise HTTPException(status_code=404, detail="Offer not found")
    logger.info(f"Offer retrieved successfully: {offer_id}")
    return offer


@router.get("/", response_model=OfferListResponse)
def list_offers(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum number of records to return"),
    title: Optional[str] = Query(None, description="Search by title"),
    db: Session = Depends(get_db)
):
    """
    List all offers with optional title search.

    - **skip**: Number of records to skip (for pagination)
    - **limit**: Maximum number of records to return
    - **title**: Optional search by title
    """
    if title:
        logger.info(f"Searching offers by title: '{title}' (skip={skip}, limit={limit})")
    else:
        logger.info(f"Listing all offers (skip={skip}, limit={limit})")

    service = OfferService(db)
    if title:
        result = service.search_offers_by_title(title, skip, limit)
    else:
        result = service.list_offers(skip, limit)

    logger.info(f"Returning {len(result.offers)} offers (total: {result.total})")
    return result


@router.put("/{offer_id}", response_model=OfferResponse)
def update_offer(
    offer_id: int,
    offer_data: OfferUpdate,
    db: Session = Depends(get_db)
):
    """
    Update an offer.

    All fields are optional. Only provided fields will be updated.
    """
    logger.info(f"Updating offer with ID: {offer_id}")
    try:
        service = OfferService(db)
        offer = service.update_offer(offer_id, offer_data)
        if not offer:
            logger.warning(f"Offer not found for update: {offer_id}")
            raise HTTPException(status_code=404, detail="Offer not found")
        logger.info(f"Offer updated successfully: {offer_id}")
        return offer
    except ValueError as e:
        logger.warning(f"Validation error updating offer {offer_id}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating offer {offer_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.delete("/{offer_id}", status_code=204)
def delete_offer(
    offer_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete an offer.
    """
    logger.info(f"Deleting offer with ID: {offer_id}")
    service = OfferService(db)
    success = service.delete_offer(offer_id)
    if not success:
        logger.warning(f"Offer not found for deletion: {offer_id}")
        raise HTTPException(status_code=404, detail="Offer not found")
    logger.info(f"Offer deleted successfully: {offer_id}")
    return None


@router.get("/influencer/{influencer_id}", response_model=InfluencerOfferListResponse)
def list_offers_for_influencer(
    influencer_id: int,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum number of records to return"),
    title: Optional[str] = Query(None, description="Search by title"),
    db: Session = Depends(get_db)
):
    """
    List offers from the perspective of a specific influencer.

    Payouts are calculated based on:
    - Custom payouts for the influencer (if they exist, takes precedence)
    - Base payout with country overrides (if no custom payout)

    - **influencer_id**: ID of the influencer
    - **skip**: Number of records to skip (for pagination)
    - **limit**: Maximum number of records to return
    - **title**: Optional search by title
    """
    logger.info(f"Fetching offers for influencer {influencer_id} (skip={skip}, limit={limit}, title={title})")
    service = OfferService(db)
    result = service.list_offers_for_influencer(influencer_id, title, skip, limit)
    logger.info(f"Returning {len(result.offers)} offers for influencer {influencer_id}")
    return result

