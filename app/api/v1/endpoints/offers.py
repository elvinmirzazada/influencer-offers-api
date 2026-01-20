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
    try:
        service = OfferService(db)
        return service.create_offer(offer_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/{offer_id}", response_model=OfferResponse)
def get_offer(
    offer_id: int,
    db: Session = Depends(get_db)
):
    """
    Get an offer by ID.
    """
    service = OfferService(db)
    offer = service.get_offer(offer_id)
    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")
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
    service = OfferService(db)
    if title:
        return service.search_offers_by_title(title, skip, limit)
    return service.list_offers(skip, limit)


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
    try:
        service = OfferService(db)
        offer = service.update_offer(offer_id, offer_data)
        if not offer:
            raise HTTPException(status_code=404, detail="Offer not found")
        return offer
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.delete("/{offer_id}", status_code=204)
def delete_offer(
    offer_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete an offer.
    """
    service = OfferService(db)
    success = service.delete_offer(offer_id)
    if not success:
        raise HTTPException(status_code=404, detail="Offer not found")
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
    service = OfferService(db)
    return service.list_offers_for_influencer(influencer_id, title, skip, limit)

