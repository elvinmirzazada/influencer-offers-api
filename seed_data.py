"""
Script to seed the database with sample data for testing.
"""
from app.core.database import SessionLocal, engine, Base
from app.models.influencer import Influencer
from app.models.offer import Offer, Payout, CountryOverride, CustomPayout, CategoryEnum, PayoutType

# Create tables
Base.metadata.create_all(bind=engine)

db = SessionLocal()

try:
    # Create sample influencers
    influencer1 = Influencer(name="Alice Johnson", email="alice@example.com")
    influencer2 = Influencer(name="Bob Smith", email="bob@example.com")
    influencer3 = Influencer(name="Carol White", email="carol@example.com")

    db.add_all([influencer1, influencer2, influencer3])
    db.commit()
    db.refresh(influencer1)
    db.refresh(influencer2)
    db.refresh(influencer3)

    print(f"✅ Created influencers:")
    print(f"  - {influencer1.name} (ID: {influencer1.id})")
    print(f"  - {influencer2.name} (ID: {influencer2.id})")
    print(f"  - {influencer3.name} (ID: {influencer3.id})")

    # Create sample offers

    # Offer 1: Gaming offer with CPA and country overrides
    offer1 = Offer(
        title="Gaming Platform Promotion",
        description="Promote our new gaming platform to your audience",
        categories="Gaming,Tech"
    )
    db.add(offer1)
    db.flush()

    payout1 = Payout(
        offer_id=offer1.id,
        payout_type=PayoutType.CPA,
        cpa_amount=20.0
    )
    db.add(payout1)
    db.flush()

    # Country overrides for offer 1
    override1_1 = CountryOverride(payout_id=payout1.id, country_code="DE", cpa_amount=30.0)
    override1_2 = CountryOverride(payout_id=payout1.id, country_code="US", cpa_amount=25.0)
    db.add_all([override1_1, override1_2])

    print(f"\n✅ Created offer: {offer1.title} (ID: {offer1.id})")
    print(f"  - Payout: $20 CPA (DE: $30, US: $25)")

    # Offer 2: Fashion offer with Fixed payout
    offer2 = Offer(
        title="Fashion Brand Campaign",
        description="Exclusive fashion brand partnership",
        categories="Fashion"
    )
    db.add(offer2)
    db.flush()

    payout2 = Payout(
        offer_id=offer2.id,
        payout_type=PayoutType.FIXED,
        fixed_amount=1000.0
    )
    db.add(payout2)

    print(f"✅ Created offer: {offer2.title} (ID: {offer2.id})")
    print(f"  - Payout: $1000 Fixed")

    # Offer 3: Health offer with CPA + Fixed
    offer3 = Offer(
        title="Health Products Promotion",
        description="Promote our health and wellness products",
        categories="Health,Nutrition"
    )
    db.add(offer3)
    db.flush()

    payout3 = Payout(
        offer_id=offer3.id,
        payout_type=PayoutType.CPA_FIXED,
        cpa_amount=15.0,
        fixed_amount=500.0
    )
    db.add(payout3)
    db.flush()

    # Country override for offer 3
    override3_1 = CountryOverride(payout_id=payout3.id, country_code="GB", cpa_amount=20.0)
    db.add(override3_1)

    print(f"✅ Created offer: {offer3.title} (ID: {offer3.id})")
    print(f"  - Payout: $15 CPA + $500 Fixed (GB: $20 CPA + $500 Fixed)")

    # Offer 4: Finance offer with CPA
    offer4 = Offer(
        title="Financial Services Promotion",
        description="Promote financial services and earn commission",
        categories="Finance"
    )
    db.add(offer4)
    db.flush()

    payout4 = Payout(
        offer_id=offer4.id,
        payout_type=PayoutType.CPA,
        cpa_amount=50.0
    )
    db.add(payout4)

    print(f"✅ Created offer: {offer4.title} (ID: {offer4.id})")
    print(f"  - Payout: $50 CPA")

    # Create custom payouts for specific influencers

    # Alice gets a custom Fixed payout for offer 1 (overrides base CPA)
    custom1 = CustomPayout(
        offer_id=offer1.id,
        influencer_id=influencer1.id,
        payout_type=PayoutType.FIXED,
        fixed_amount=2000.0
    )
    db.add(custom1)

    print(f"\n✅ Created custom payout:")
    print(f"  - {influencer1.name} gets $2000 Fixed for '{offer1.title}'")
    print(f"    (Overrides base $20-$30 CPA)")

    # Bob gets a custom CPA for offer 3 (overrides base CPA+Fixed)
    custom2 = CustomPayout(
        offer_id=offer3.id,
        influencer_id=influencer2.id,
        payout_type=PayoutType.CPA,
        cpa_amount=100.0
    )
    db.add(custom2)

    print(f"  - {influencer2.name} gets $100 CPA for '{offer3.title}'")
    print(f"    (Overrides base $15-$20 CPA + $500 Fixed)")

    db.commit()

    print("\n" + "="*60)
    print("✅ Database seeded successfully!")
    print("="*60)
    print("\nYou can now:")
    print(f"  - List all offers for Alice (ID: {influencer1.id}): GET /api/v1/offers/influencer/{influencer1.id}")
    print(f"  - List all offers for Bob (ID: {influencer2.id}): GET /api/v1/offers/influencer/{influencer2.id}")
    print(f"  - List all offers for Carol (ID: {influencer3.id}): GET /api/v1/offers/influencer/{influencer3.id}")
    print("  - Search offers: GET /api/v1/offers/?title=Gaming")

except Exception as e:
    print(f"❌ Error seeding database: {e}")
    db.rollback()
finally:
    db.close()

