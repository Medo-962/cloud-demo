import googlemaps
from config import Config

def get_gmaps_client():
    if not Config.GOOGLE_MAPS_API_KEY:
        raise ValueError("Google Maps API key is not configured.")
    return googlemaps.Client(key=Config.GOOGLE_MAPS_API_KEY)

def calculate_distance_time(origin, destination):
    """
    origin: string (address or 'lat,lng')
    destination: string (address or 'lat,lng')
    Returns: (distance_km, duration_min) or (None, None) on error
    """
    try:
        gmaps = get_gmaps_client()
        result = gmaps.distance_matrix(origins=origin, destinations=destination, mode="driving")
        
        if result['status'] == 'OK' and result['rows'][0]['elements'][0]['status'] == 'OK':
            element = result['rows'][0]['elements'][0]
            # distance is returned in meters
            distance_meters = element['distance']['value']
            # duration is returned in seconds
            duration_seconds = element['duration']['value']
            
            distance_km = distance_meters / 1000.0
            duration_min = duration_seconds / 60.0
            
            return distance_km, duration_min
    except Exception as e:
        print(f"Error calculating distance: {e}")
        
    return None, None

def get_directions_route(origin, destination):
    """
    Returns the optimal route (encoded polyline points) for Map drawing.
    """
    try:
        gmaps = get_gmaps_client()
        result = gmaps.directions(origin, destination, mode="driving")
        if result:
            route = result[0]
            polyline = route['overview_polyline']['points']
            return {"polyline": polyline}
    except Exception as e:
        print(f"Error fetching route: {e}")
    return None

