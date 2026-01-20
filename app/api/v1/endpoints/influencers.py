from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.repositories.influencer_repository import InfluencerRepository
from app.schemas.influencer import InfluencerResponse

router = APIRouter()


@router.get("/", response_model=List[InfluencerResponse])
def list_influencers(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum number of records to return"),
    db: Session = Depends(get_db)
):
    """
    List all influencers with pagination.

    - **skip**: Number of records to skip (for pagination)
    - **limit**: Maximum number of records to return (max: 100)

    Returns a list of influencers with their basic information.
    """
    try:
        repository = InfluencerRepository(db)
        influencers = repository.get_all(skip=skip, limit=limit)
        return influencers
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/{influencer_id}", response_model=InfluencerResponse)
def get_influencer(
    influencer_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific influencer by ID.

    - **influencer_id**: The ID of the influencer

    Returns the influencer details if found.
    """
    try:
        repository = InfluencerRepository(db)
        influencer = repository.get_by_id(influencer_id)
        if not influencer:
            raise HTTPException(status_code=404, detail="Influencer not found")
        return influencer
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

