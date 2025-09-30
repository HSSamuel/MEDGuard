import sqlite3
import json
import random
from pathlib import Path

# This should be the same path as in your config
DB_PATH = Path(__file__).resolve().parent.parent / "medguard.db"
OUTPUT_PATH = Path(__file__).resolve().parent / "predicted_hotspots.json"

def get_existing_hotspots():
    """Fetches the locations of existing reports from the database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("""
        SELECT latitude, longitude
        FROM reports
        WHERE latitude IS NOT NULL AND longitude IS NOT NULL
    """)
    rows = c.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def predict_future_hotspots(existing_hotspots):
    """
    A simulation of a machine learning model.
    It generates new potential hotspots near existing ones.
    """
    predictions = []
    if not existing_hotspots:
        # If there's no data, create some default predictions for Nigeria
        return [
            {"latitude": 9.0820, "longitude": 8.6753, "risk_level": 0.75, "area": "Abuja"},
            {"latitude": 6.5244, "longitude": 3.3792, "risk_level": 0.85, "area": "Lagos"},
        ]

    for spot in existing_hotspots:
        # Create a new predicted hotspot with a slight random offset
        new_lat = spot["latitude"] + random.uniform(-0.05, 0.05)
        new_lon = spot["longitude"] + random.uniform(-0.05, 0.05)
        
        predictions.append({
            "latitude": new_lat,
            "longitude": new_lon,
            "risk_level": round(random.uniform(0.6, 0.95), 2),
            "area": "Predicted Hotspot"
        })
    
    return predictions

def run_prediction_model():
    """
    Main function to run the model and save the results.
    """
    existing = get_existing_hotspots()
    predicted = predict_future_hotspots(existing)
    
    with open(OUTPUT_PATH, 'w') as f:
        json.dump(predicted, f, indent=4)
        
    print(f"✅ Predictive model run successfully. {len(predicted)} hotspots predicted.")

if __name__ == "__main__":
    run_prediction_model()