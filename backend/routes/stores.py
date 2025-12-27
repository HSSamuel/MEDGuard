import requests
from flask import Blueprint, request, jsonify, current_app
# import redis # REMOVED REDIS IMPORT
# from backend.config import get_config # REMOVED

stores_bp = Blueprint("stores_api", __name__)

# redis_client = None # Caching is disabled, so client is ignored

@stores_bp.route("/pharmacies/nearby")
def get_nearby_pharmacies():
    """
    Finds nearby pharmacies using the Google Places API.
    NOTE: Caching is DISABLED in this version to avoid Redis dependency.
    This will result in slow synchronous calls (~7.8 seconds).
    """
    user_lat = request.args.get("lat")
    user_lon = request.args.get("lon")

    if not user_lat or not user_lon:
        return jsonify({"error": "Latitude and longitude are required."}), 400

    # Get the API key securely from the app's configuration
    api_key = current_app.config.get("GOOGLE_API_KEY")
    if not api_key or "your_google_api_key" in api_key:
        print("ERROR: Google API Key is not configured.")
        # Return empty list instead of 500 so the frontend doesn't crash
        return jsonify([])

    # This is the URL for Google's "Nearby Search" API
    search_url = (
        f"https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        f"?location={user_lat},{user_lon}"
        f"&radius=5000"  # Search within a 5-kilometer radius
        f"&type=pharmacy"
        f"&key={api_key}"
    )

    try:
        # Make the request to the Google Places API
        # THIS IS THE BLOCKING CALL THAT WILL BE SLOW
        response = requests.get(search_url, timeout=10)
        response.raise_for_status()  # This will raise an error for bad responses (like 4xx or 5xx)
        results = response.json().get("results", [])

        # We will format the results to send only what our frontend needs
        pharmacies = [
            {
                "name": place.get("name"),
                "address": place.get("vicinity", "Address not available"),
                "rating": place.get("rating", "Not Rated"),
                "lat": place.get("geometry", {}).get("location", {}).get("lat"),
                "lng": place.get("geometry", {}).get("location", {}).get("lng"),
            }
            for place in results
        ]

        return jsonify(pharmacies)

    except requests.exceptions.RequestException as e:
        # Log the error for debugging and return a generic error to the user
        print(f"Error calling Google Places API (SLOW MODE): {e}")
        return jsonify({"error": "Failed to fetch pharmacy data from the external service."}), 502