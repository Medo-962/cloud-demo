import math
import googlemaps
from config import Config

def get_gmaps_client():
    if not Config.GOOGLE_MAPS_API_KEY:
        return None
    return googlemaps.Client(key=Config.GOOGLE_MAPS_API_KEY)

def _haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate straight-line distance in km using the Haversine formula."""
    R = 6371.0
    lat1_r, lon1_r = math.radians(lat1), math.radians(lon1)
    lat2_r, lon2_r = math.radians(lat2), math.radians(lon2)
    dlat = lat2_r - lat1_r
    dlon = lon2_r - lon1_r
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1_r) * math.cos(lat2_r) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def _parse_latlng(value):
    """Try to parse 'lat,lng' string into (float, float). Returns None on failure."""
    try:
        parts = value.split(',')
        if len(parts) == 2:
            return float(parts[0].strip()), float(parts[1].strip())
    except (ValueError, AttributeError):
        pass
    return None

def calculate_distance_time(origin, destination):
    """
    origin: string (address or 'lat,lng')
    destination: string (address or 'lat,lng')
    Returns: (distance_km, duration_min) or (None, None) on error
    """
    # Try Google Maps first
    gmaps = get_gmaps_client()
    if gmaps:
        try:
            result = gmaps.distance_matrix(origins=origin, destinations=destination, mode="driving")
            
            if result['status'] == 'OK' and result['rows'][0]['elements'][0]['status'] == 'OK':
                element = result['rows'][0]['elements'][0]
                distance_meters = element['distance']['value']
                duration_seconds = element['duration']['value']
                
                distance_km = distance_meters / 1000.0
                duration_min = duration_seconds / 60.0
                
                return distance_km, duration_min
        except Exception as e:
            print(f"Google Maps API error: {e}")

    # Fallback: Haversine calculation from lat,lng pairs
    origin_coords = _parse_latlng(origin)
    dest_coords = _parse_latlng(destination)

    if origin_coords and dest_coords:
        straight_km = _haversine_distance(
            origin_coords[0], origin_coords[1],
            dest_coords[0], dest_coords[1]
        )
        # Multiply by 1.3 to approximate road distance
        road_km = straight_km * 1.3
        # Estimate ~40 km/h average city driving speed
        duration_min = (road_km / 40.0) * 60.0
        print(f"Using Haversine fallback: {round(road_km, 2)} km, {round(duration_min, 2)} min")
        return road_km, duration_min

    return None, None

def get_directions_route(origin, destination):
    """
    Returns the optimal route (encoded polyline points) for Map drawing.
    """
    gmaps = get_gmaps_client()
    if not gmaps:
        return None
    try:
        result = gmaps.directions(origin, destination, mode="driving")
        if result:
            route = result[0]
            polyline = route['overview_polyline']['points']
            return {"polyline": polyline}
    except Exception as e:
        print(f"Error fetching route: {e}")
    return None

