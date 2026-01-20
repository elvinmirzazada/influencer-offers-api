from fastapi import APIRouter
from app.api.v1.endpoints import offers, influencers

api_router = APIRouter()
api_router.include_router(offers.router, prefix="/offers", tags=["offers"])
api_router.include_router(influencers.router, prefix="/influencers", tags=["influencers"])

