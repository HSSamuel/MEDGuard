from flask import Blueprint, jsonify
from backend.database import get_db
import random
from datetime import datetime, timedelta

hotspot_bp = Blueprint("hotspot_api", __name__)

@hotspot_bp.route('/hotspots', methods=['GET'])
def get_hotspots():
    """
    API endpoint to retrieve LIVE hotspot data for the map (existing reports).
    """
    conn = get_db()
    # Fetch locations with coordinates
    rows = conn.execute("""
        SELECT latitude, longitude, drug_name, batch_number, reported_on
        FROM reports
        WHERE latitude IS NOT NULL AND longitude IS NOT NULL
    """).fetchall()
    
    hotspots = [dict(row) for row in rows]
    return jsonify(hotspots)

@hotspot_bp.route('/predicted-hotspots', methods=['GET'])
def get_predicted_hotspots():
    """
    Simulates fetching AI-predicted future hotspot locations.
    """
    # --- Mock AI Prediction Data ---
    predicted_spots = [
        # Lagos (high density area)
        {"latitude": 6.4531, "longitude": 3.3958, "area": "Lekki Phase 1, Lagos", "risk_level": random.uniform(0.7, 0.9)},
        # Abuja (Federal Capital Territory)
        {"latitude": 9.0765, "longitude": 7.3986, "area": "Central Area, Abuja", "risk_level": random.uniform(0.5, 0.8)},
        # Kano (Northern region hub)
        {"latitude": 11.9961, "longitude": 8.5165, "area": "Sabon Gari, Kano", "risk_level": random.uniform(0.6, 0.85)},
    ]
    return jsonify(predicted_spots)