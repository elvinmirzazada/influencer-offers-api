import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.core.database import Base, get_db
from app.models.offer import CategoryEnum, PayoutType

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override get_db dependency for testing."""
    db_local = None
    try:
        db_local = TestingSessionLocal()
        yield db_local
    finally:
        db_local.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_database():
    """Create and clean up test database for each test."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_create_offer_with_cpa_payout():
    """Test creating an offer with CPA payout."""
    offer_data = {
        "title": "Gaming Offer",
        "description": "Promote our gaming platform",
        "categories": ["Gaming", "Tech"],
        "payout": {
            "payout_type": "CPA",
            "cpa_amount": 20.0,
            "country_overrides": [
                {"country_code": "DE", "cpa_amount": 30.0},
                {"country_code": "US", "cpa_amount": 25.0}
            ]
        }
    }

    response = client.post("/api/v1/offers/", json=offer_data)
    assert response.status_code == 201

    data = response.json()
    assert data["title"] == "Gaming Offer"
    assert data["description"] == "Promote our gaming platform"
    assert len(data["categories"]) == 2
    assert data["payout"]["payout_type"] == "CPA"
    assert data["payout"]["cpa_amount"] == 20.0
    assert len(data["payout"]["country_overrides"]) == 2


def test_create_offer_with_fixed_payout():
    """Test creating an offer with Fixed payout."""
    offer_data = {
        "title": "Fashion Campaign",
        "description": "Promote fashion brand",
        "categories": ["Fashion"],
        "payout": {
            "payout_type": "FIXED",
            "fixed_amount": 1000.0
        }
    }

    response = client.post("/api/v1/offers/", json=offer_data)
    assert response.status_code == 201

    data = response.json()
    assert data["payout"]["payout_type"] == "FIXED"
    assert data["payout"]["fixed_amount"] == 1000.0
    assert data["payout"]["cpa_amount"] is None


def test_create_offer_with_cpa_fixed_payout():
    """Test creating an offer with CPA + Fixed payout."""
    offer_data = {
        "title": "Health Offer",
        "description": "Promote health products",
        "categories": ["Health", "Nutrition"],
        "payout": {
            "payout_type": "CPA_FIXED",
            "cpa_amount": 15.0,
            "fixed_amount": 500.0
        }
    }

    response = client.post("/api/v1/offers/", json=offer_data)
    assert response.status_code == 201

    data = response.json()
    assert data["payout"]["payout_type"] == "CPA_FIXED"
    assert data["payout"]["cpa_amount"] == 15.0
    assert data["payout"]["fixed_amount"] == 500.0


def test_get_offer():
    """Test getting an offer by ID."""
    # Create an offer first
    offer_data = {
        "title": "Test Offer",
        "description": "Test description",
        "categories": ["Gaming"],
        "payout": {
            "payout_type": "CPA",
            "cpa_amount": 10.0
        }
    }
    create_response = client.post("/api/v1/offers/", json=offer_data)
    offer_id = create_response.json()["id"]

    # Get the offer
    response = client.get(f"/api/v1/offers/{offer_id}")
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == offer_id
    assert data["title"] == "Test Offer"


def test_get_nonexistent_offer():
    """Test getting a non-existent offer."""
    response = client.get("/api/v1/offers/999")
    assert response.status_code == 404


def test_list_offers():
    """Test listing offers."""
    # Create multiple offers
    for i in range(3):
        offer_data = {
            "title": f"Offer {i}",
            "description": f"Description {i}",
            "categories": ["Gaming"],
            "payout": {
                "payout_type": "CPA",
                "cpa_amount": 10.0 + i
            }
        }
        client.post("/api/v1/offers/", json=offer_data)

    # List all offers
    response = client.get("/api/v1/offers/")
    assert response.status_code == 200

    data = response.json()
    assert data["total"] == 3
    assert len(data["offers"]) == 3


def test_search_offers_by_title():
    """Test searching offers by title."""
    # Create offers with different titles
    offers = [
        {"title": "Gaming Platform", "description": "Test", "categories": ["Gaming"],
         "payout": {"payout_type": "CPA", "cpa_amount": 10.0}},
        {"title": "Fashion Brand", "description": "Test", "categories": ["Fashion"],
         "payout": {"payout_type": "FIXED", "fixed_amount": 500.0}},
        {"title": "Gaming Console", "description": "Test", "categories": ["Gaming"],
         "payout": {"payout_type": "CPA", "cpa_amount": 15.0}},
    ]

    for offer in offers:
        client.post("/api/v1/offers/", json=offer)

    # Search for "Gaming"
    response = client.get("/api/v1/offers/?title=Gaming")
    assert response.status_code == 200

    data = response.json()
    assert data["total"] == 2
    assert all("Gaming" in offer["title"] for offer in data["offers"])


def test_update_offer():
    """Test updating an offer."""
    # Create an offer
    offer_data = {
        "title": "Original Title",
        "description": "Original description",
        "categories": ["Gaming"],
        "payout": {
            "payout_type": "CPA",
            "cpa_amount": 10.0
        }
    }
    create_response = client.post("/api/v1/offers/", json=offer_data)
    offer_id = create_response.json()["id"]

    # Update the offer
    update_data = {
        "title": "Updated Title",
        "description": "Updated description"
    }
    response = client.put(f"/api/v1/offers/{offer_id}", json=update_data)
    assert response.status_code == 200

    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["description"] == "Updated description"


def test_delete_offer():
    """Test deleting an offer."""
    # Create an offer
    offer_data = {
        "title": "To Delete",
        "description": "This will be deleted",
        "categories": ["Gaming"],
        "payout": {
            "payout_type": "CPA",
            "cpa_amount": 10.0
        }
    }
    create_response = client.post("/api/v1/offers/", json=offer_data)
    offer_id = create_response.json()["id"]

    # Delete the offer
    response = client.delete(f"/api/v1/offers/{offer_id}")
    assert response.status_code == 204

    # Verify it's deleted
    get_response = client.get(f"/api/v1/offers/{offer_id}")
    assert get_response.status_code == 404


def test_invalid_payout_cpa_missing_amount():
    """Test that CPA payout requires cpa_amount."""
    offer_data = {
        "title": "Invalid Offer",
        "description": "Missing CPA amount",
        "categories": ["Gaming"],
        "payout": {
            "payout_type": "CPA"
        }
    }

    response = client.post("/api/v1/offers/", json=offer_data)
    assert response.status_code == 400

