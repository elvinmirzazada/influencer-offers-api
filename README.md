# Influencer Offers API

Backend API for the Influencer Offers system built with FastAPI.

## Features

- ✅ **Offer Management**: Create, update, delete, and list offers
- ✅ **Flexible Payout System**: Support for CPA, Fixed, and CPA+Fixed payouts
- ✅ **Country-Specific Overrides**: Define different CPA amounts per country
- ✅ **Custom Influencer Payouts**: Override base payouts for specific influencers
- ✅ **Influencer View**: List offers with personalized payout information
- ✅ **Search Functionality**: Search offers by title
- ✅ **Clean Architecture**: Repository pattern with separate business logic layer
- ✅ **Dockerized**: Production-ready Docker setup with docker-compose

## Project Structure

```
influencer-offers-api/
├── app/
│   ├── core/              # Core configuration (database, config)
│   ├── models/            # SQLAlchemy models with TimestampMixin
│   │   ├── base.py        # Base models and mixins
│   │   ├── offer.py       # Offer, Payout, CountryOverride, CustomPayout
│   │   └── influencer.py  # Influencer model
│   ├── schemas/           # Pydantic schemas (request/response)
│   │   ├── base.py        # Base schemas with timestamps
│   │   ├── offer.py       # Offer schemas
│   │   ├── payout.py      # Payout schemas
│   │   └── influencer.py  # Influencer schemas
│   ├── repositories/      # Database layer (CRUD operations)
│   │   ├── offer_repository.py
│   │   └── influencer_repository.py
│   ├── services/          # Business logic layer
│   │   └── offer_service.py
│   └── api/               # API routes
│       ├── deps.py        # Dependencies
│       └── v1/
│           ├── api.py
│           └── endpoints/
│               └── offers.py
├── tests/                 # Test files
│   └── test_offers.py
├── seed_data.py          # Script to populate sample data
└── requirements.txt      # Python dependencies
└── Dockerfile            # Dockerfile
└── docker-compose.yml    # Docker Compose configuration
```

## Setup

### Option 1: Docker (Recommended)

#### Prerequisites
- Docker installed on your system
- Docker Compose installed

#### Quick Start

1. **Clone the repository and navigate to the project:**
```bash
cd influencer-offers-api
```

2. **Create data directory (for persistent database):**
```bash
mkdir -p data
```

3. **Build and run with Docker Compose:**
```bash
docker-compose up -d
```

The API will be available at `http://localhost:8000`

API documentation will be available at `http://localhost:8000/docs`

4. **(Optional) Seed the database with sample data:**
```bash
docker-compose exec api python seed_data.py
```

This will create:
- 3 sample influencers (Alice, Bob, Carol)
- 4 sample offers with different payout types
- 2 custom payouts for specific influencers

---

### Option 2: Local Development (Without Docker)

#### 1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

#### 2. Install dependencies:
```bash
pip install -r requirements.txt
```

#### 3. Create a `.env` file:
```bash
cp .env.example .env
```

Or the `.env` file is already created with default values.

#### 4. (Optional) Seed the database with sample data:
```bash
python seed_data.py
```

This will create:
- 3 sample influencers (Alice, Bob, Carol)
- 4 sample offers with different payout types
- 2 custom payouts for specific influencers

#### 5. Run the application:
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

API documentation will be available at `http://localhost:8000/docs`

## Architecture

### Layered Architecture:
- **Models**: SQLAlchemy database models (ORM)
- **Schemas**: Pydantic models for validation and serialization
- **Repositories**: Handle database operations (CRUD) - no business logic
- **Services**: Contain business logic - interact with repositories
- **API Endpoints**: Handle HTTP requests/responses - use services

### Key Design Decisions:
1. **TimestampSchema**: Response schemas extend a base schema for timestamps
2. **Repository Pattern**: Database operations are isolated from business logic
3. **Service Layer**: Complex payout calculations and business rules

## API Endpoints

### Offers

- **POST** `/api/v1/offers/` - Create a new offer
- **GET** `/api/v1/offers/{offer_id}` - Get offer by ID
- **GET** `/api/v1/offers/` - List all offers (with optional title search)
- **PUT** `/api/v1/offers/{offer_id}` - Update an offer
- **DELETE** `/api/v1/offers/{offer_id}` - Delete an offer
- **GET** `/api/v1/offers/influencer/{influencer_id}` - List offers for specific influencer
- **GET** `/api/v1/influencers` - List influencers

### Examples

#### Create an Offer with CPA Payout:
```bash
curl -X POST "http://localhost:8000/api/v1/offers/" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Gaming Platform Promotion",
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
  }'
```

#### List Offers for an Influencer:
```bash
curl "http://localhost:8000/api/v1/offers/influencer/1"
```

#### Search Offers by Title:
```bash
curl "http://localhost:8000/api/v1/offers/?title=Gaming"
```

## Payout Logic

### Payout Types:
1. **CPA**: Pay per conversion
   - Supports country-specific overrides
   - Display: "$20 - $30 CPA" (shows range if overrides exist)

2. **Fixed**: One-time payment
   - No country overrides
   - Display: "$1000 Fixed"

3. **CPA + Fixed**: Combination of both
   - CPA supports country overrides
   - Display: "$15 - $20 CPA + $500 Fixed"

### Custom Payout Precedence:
- If a custom payout exists for an influencer, it **completely overrides** the base payout
- Country overrides are **not applied** to custom payouts
- Example: If base is "\$20" CPA with DE override "\$30", but influencer has custom "\$1000 Fixed", they only see "\$1000 Fixed"

## Running Tests

```bash
pytest
```

To run with coverage:
```bash
pytest --cov=app tests/
```

## Development

The application uses:
- **FastAPI**: Modern, fast web framework
- **SQLAlchemy**: SQL toolkit and ORM
- **Pydantic**: Data validation using Python type annotations
- **SQLite**: Lightweight database (can be changed to PostgreSQL/MySQL)

## Next Steps

To extend this API, consider:
- Adding authentication and authorization
- Creating influencer registration/management endpoints
- Adding analytics and reporting
- Implementing rate limiting
- Adding more comprehensive error handling
- Setting up database migrations with Alembic

