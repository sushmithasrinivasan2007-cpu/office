from flask import Blueprint, request, jsonify
from geopy.distance import geodesic
from geopy.geocoders import Nominatim
import requests
from utils.supabase_client import supabase
from datetime import datetime

geo_bp = Blueprint('geo_bp', __name__)

OSM_BASE_URL = "https://nominatim.openstreetmap.org"

@geo_bp.route('/verify', methods=['POST'])
def geo_verify():
    try:
        data = request.json
        user_lat = data.get('user_lat')
        user_lng = data.get('user_lng')
        task_lat = data.get('task_lat')
        task_lng = data.get('task_lng')
        radius_meters = data.get('radius', 100)

        if None in [user_lat, user_lng, task_lat, task_lng]:
            return jsonify({"error": "Missing location coordinates"}), 400

        user_loc = (float(user_lat), float(user_lng))
        task_loc = (float(task_lat), float(task_lng))

        distance = geodesic(user_loc, task_loc).meters
        is_verified = distance <= radius_meters

        return jsonify({
            "verified": is_verified,
            "distance_meters": round(distance, 2),
            "allowed_radius": radius_meters,
            "message": "Location verified" if is_verified else f"Too far: {round(distance, 2)}m > {radius_meters}m"
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@geo_bp.route('/reverse-geocode', methods=['GET'])
def reverse_geocode():
    """Convert coordinates to address using OSM"""
    try:
        lat = request.args.get('lat')
        lng = request.args.get('lng')

        if not lat or not lng:
            return jsonify({"error": "lat and lng required"}), 400

        response = requests.get(
            f"{OSM_BASE_URL}/reverse",
            params={'lat': lat, 'lon': lng, 'format': 'json'},
            headers={'User-Agent': 'SmartOfficeOS/1.0'}
        )

        if response.status_code == 200:
            data = response.json()
            address = data.get('display_name', 'Unknown location')
            return jsonify({"address": address, "coordinates": {"lat": lat, "lng": lng}}), 200

        return jsonify({"error": "Geocoding failed"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@geo_bp.route('/geocode', methods=['GET'])
def geocode():
    """Convert address to coordinates using OSM"""
    try:
        address = request.args.get('address')
        if not address:
            return jsonify({"error": "address parameter required"}), 400

        response = requests.get(
            f"{OSM_BASE_URL}/search",
            params={'q': address, 'format': 'json', 'limit': 5},
            headers={'User-Agent': 'SmartOfficeOS/1.0'}
        )

        if response.status_code == 200:
            results = response.json()
            return jsonify({"results": [
                {
                    "lat": r['lat'],
                    "lng": r['lon'],
                    "display_name": r['display_name'],
                    "type": r['type']
                } for r in results
            ]}), 200

        return jsonify({"error": "Geocoding failed"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@geo_bp.route('/verify-attendance', methods=['POST'])
def verify_attendance_geo():
    """Verify attendance check-in location against company geofence"""
    try:
        data = request.json
        user_id = data.get('user_id')
        company_id = data.get('company_id')
        user_lat = data.get('latitude')
        user_lng = data.get('longitude')

        # Get company office location (stored in settings)
        settings_res = supabase.table('company_settings').select('*').eq('company_id', company_id).execute()
        if settings_res.data:
            settings = settings_res.data[0]
            office_lat = settings.get('office_latitude')
            office_lng = settings.get('office_longitude')
            office_radius = settings.get('office_radius_meters', 500)

            if office_lat and office_lng:
                distance = geodesic((user_lat, user_lng), (office_lat, office_lng)).meters
                if distance <= office_radius:
                    return jsonify({"verified": True, "distance": round(distance, 2)}), 200
                else:
                    return jsonify({
                        "verified": False,
                        "distance": round(distance, 2),
                        "message": f"Outside office geofence by {round(distance - office_radius, 2)}m"
                    }), 200

        # No geofence set, allow any location
        return jsonify({"verified": True, "note": "No geofence configured"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
