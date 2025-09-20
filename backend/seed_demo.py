"""
Seed the MedGuard database with demo data for hackathon presentations.
Run this once before the demo:  python -m backend.seed_demo
"""

from datetime import datetime, timedelta
# Import the create_app function to create an application context
from backend.app import create_app
from backend.database import init_db, get_db
from backend.models import insert_drug

def seed():
    # Create a Flask app instance to establish an application context
    app = create_app()
    with app.app_context():
        # All database operations must happen inside this 'with' block
        init_db()
        conn = get_db()
        c = conn.cursor()

        # Clear existing data for a clean slate
        print("Clearing existing drug and report data...")
        c.execute("DELETE FROM drugs")
        c.execute("DELETE FROM reports")
        conn.commit()

        today = datetime.now()

        # A list of demo drugs to insert
        demo_batches = [
            {
                "name": "Amartem",
                "batch_number": "BATCH-VALID-001",
                "mfg_date": (today - timedelta(days=180)).strftime("%Y-%m-%d"),
                "expiry_date": (today + timedelta(days=365)).strftime("%Y-%m-%d"),
                "manufacturer": "HealthFirst Pharma"
            },
            {
                "name": "Paracetamol",
                "batch_number": "BATCH-EXPIRED-002",
                "mfg_date": (today - timedelta(days=730)).strftime("%Y-%m-%d"),
                "expiry_date": (today - timedelta(days=30)).strftime("%Y-%m-%d"),
                "manufacturer": "CareWell Labs"
            },
            {
                "name": "Vitamin C",
                "batch_number": "BATCH-SOON-003",
                "mfg_date": (today - timedelta(days=340)).strftime("%Y-%m-%d"),
                "expiry_date": (today + timedelta(days=25)).strftime("%Y-%m-%d"),
                "manufacturer": "BioHealth Corp"
            }
        ]

        print("Inserting demo drugs...")
        for drug in demo_batches:
            try:
                insert_drug(**drug)
                print(f"  -> Inserted: {drug['name']} ({drug['batch_number']})")
            except Exception as e:
                print(f"  -> Skipping {drug['batch_number']}: {e}")

        print("Inserting demo reports...")
        c.execute(
            "INSERT INTO reports (batch_number, location, note, drug_name) VALUES (?, ?, ?, ?)",
            ("FAKE-BATCH-999", "Abuja", "Counterfeit packaging detected", "Unknown Drug")
        )
        c.execute(
            "INSERT INTO reports (batch_number, location, note, drug_name) VALUES (?, ?, ?, ?)",
            ("BATCH-EXPIRED-002", "Lagos", "Expired stock found in market", "Paracetamol")
        )
        
        conn.commit()

    print("\n✅ Demo data seeded successfully.")


if __name__ == "__main__":
    seed()