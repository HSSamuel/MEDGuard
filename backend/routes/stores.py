import requests
from flask import Blueprint, request, jsonify, current_app

# Create a new Blueprint for our stores API
stores_bp = Blueprint("stores_api", __name__)

@stores_bp.route("/pharmacies/nearby")
def get_nearby_pharmacies():
    """
    Finds nearby pharmacies using the Google Places API.
    Requires 'lat' and 'lon' as query parameters from the frontend.
    """
    user_lat = request.args.get("lat")
    user_lon = request.args.get("lon")

    if not user_lat or not user_lon:
        return jsonify({"error": "Latitude and longitude are required."}), 400

    # Get the API key securely from the app's configuration
    api_key = current_app.config.get("GOOGLE_API_KEY")
    if not api_key or "your_google_api_key" in api_key:
        print("ERROR: Google API Key is not configured.")
        return jsonify({"error": "This feature is not configured on the server."}), 500

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
        print(f"Error calling Google Places API: {e}")
        return jsonify({"error": "Failed to fetch pharmacy data from the external service."}), 502