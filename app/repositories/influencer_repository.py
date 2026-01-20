from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.influencer import Influencer
from app.schemas.influencer import InfluencerCreate, InfluencerUpdate


class InfluencerRepository:
    """Repository for Influencer CRUD operations."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, influencer_data: InfluencerCreate) -> Influencer:
        """Create a new influencer."""
        db_influencer = Influencer(
            name=influencer_data.name,
            email=influencer_data.email
        )
        self.db.add(db_influencer)
        self.db.commit()
        self.db.refresh(db_influencer)
        return db_influencer

    def get_by_id(self, influencer_id: int) -> Optional[Influencer]:
        """Get influencer by ID."""
        return self.db.query(Influencer).filter(Influencer.id == influencer_id).first()

    def get_by_email(self, email: str) -> Optional[Influencer]:
        """Get influencer by email."""
        return self.db.query(Influencer).filter(Influencer.email == email).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[Influencer]:
        """Get all influencers with pagination."""
        return self.db.query(Influencer).offset(skip).limit(limit).all()

    def update(self, influencer_id: int, influencer_data: InfluencerUpdate) -> Optional[Influencer]:
        """Update an influencer."""
        db_influencer = self.get_by_id(influencer_id)
        if not db_influencer:
            return None

        if influencer_data.name is not None:
            db_influencer.name = influencer_data.name
        if influencer_data.email is not None:
            db_influencer.email = influencer_data.email

        self.db.commit()
        self.db.refresh(db_influencer)
        return db_influencer

    def delete(self, influencer_id: int) -> bool:
        """Delete an influencer."""
        db_influencer = self.get_by_id(influencer_id)
        if not db_influencer:
            return False

        self.db.delete(db_influencer)
        self.db.commit()
        return True

