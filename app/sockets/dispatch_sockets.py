import math
import eventlet
from app.__init__ import socketio
from app.sockets.driver_sockets import ACTIVE_DRIVERS, get_user_from_token
from app.services.ride_service import update_ride_status

# A dictionary to track which rides are currently being dispatched
# {ride_id: {"status": "pending", "declined_drivers": set()}}
DISPATCH_QUEUE = {}

def calculate_haversine(lat1, lon1, lat2, lon2):
    R = 6371.0 # Radius of Earth in km
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    dlon = lon2_rad - lon1_rad
    dlat = lat2_rad - lat1_rad
    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    return distance

def find_nearest_available_driver(pickup_lat, pickup_lng, declined_drivers):
    nearest_driver_id = None
    min_distance = float('inf')
    
    for driver_id, location in ACTIVE_DRIVERS.items():
        if driver_id in declined_drivers:
            continue
            
        if location['lat'] is None or location['lng'] is None:
            continue
            
        distance = calculate_haversine(pickup_lat, pickup_lng, location['lat'], location['lng'])
        if distance < min_distance and distance <= 5.0: # Only look within 5km
            min_distance = distance
            nearest_driver_id = driver_id
            
    return nearest_driver_id

def dispatch_ride(ride_id, ride_data):
    """
    Runs in the background. Finds nearest driver, emits event, waits 15s.
    """
    DISPATCH_QUEUE[ride_id] = {"status": "pending", "declined_drivers": set(), "rider_id": ride_data.get('rider_id')}
    
    def process_dispatch():
        pickup_lat = float(ride_data['pickupLat'])
        pickup_lng = float(ride_data['pickupLng'])
        
        while DISPATCH_QUEUE[ride_id]['status'] == 'pending':
            declined = DISPATCH_QUEUE[ride_id]['declined_drivers']
            driver_id = find_nearest_available_driver(pickup_lat, pickup_lng, declined)
            
            if not driver_id:
                # No drivers available
                print(f"No available drivers for ride {ride_id}")
                socketio.emit('ride_no_drivers', {"rideID": ride_id}, room=f"rider_{ride_data.get('rider_id')}")
                DISPATCH_QUEUE[ride_id]['status'] = 'failed'
                break
                
            print(f"Pinging driver {driver_id} for ride {ride_id}")
            socketio.emit('new_ride_request', ride_data, room=f"driver_{driver_id}")
            
            # Wait 15 seconds for acceptance
            eventlet.sleep(15)
            
            if DISPATCH_QUEUE[ride_id]['status'] == 'accepted':
                break # Driver accepted, loop exits
                
            if DISPATCH_QUEUE.get(ride_id, {}).get('status') == 'pending':
                # Driver didn't accept in time or explicitly declined
                print(f"Driver {driver_id} didn't accept ride {ride_id}. Trying next.")
                DISPATCH_QUEUE[ride_id]['declined_drivers'].add(driver_id)
                # Inform driver they missed it
                socketio.emit('ride_request_timeout', {"rideID": ride_id}, room=f"driver_{driver_id}")

    # Launch as background thread
    eventlet.spawn(process_dispatch)

@socketio.on('accept_ride')
def handle_accept_ride(data):
    """
    Driver emits this when they accept the ride.
    data = {"rideID": 123, "token": ...}
    """
    user = get_user_from_token(data.get('token'))
    if not user or user['role'] != 'driver':
        return
        
    ride_id = data.get('rideID')
    driver_id = user['id']
    
    if ride_id in DISPATCH_QUEUE and DISPATCH_QUEUE[ride_id]['status'] == 'pending':
        # Mark as accepted to stop the dispatch loop
        DISPATCH_QUEUE[ride_id]['status'] = 'accepted'
        
        # Update DB
        res, code = update_ride_status(ride_id, driver_id, 'accepted')
        
        if code == 200:
            # Emit success to driver
            socketio.emit('ride_accepted_success', {"rideID": ride_id}, room=f"driver_{driver_id}")
            
            # Emit notification to rider
            rider_id = DISPATCH_QUEUE[ride_id].get('rider_id')
            if rider_id:
                socketio.emit('driver_accepted', {
                    "rideID": ride_id, 
                    "driverID": driver_id,
                    "driverName": user.get('fullName'), # Might need to query DB for full driver details
                    "driverLat": ACTIVE_DRIVERS.get(driver_id, {}).get('lat'),
                    "driverLng": ACTIVE_DRIVERS.get(driver_id, {}).get('lng')
                }, room=f"rider_{rider_id}")
                
                # Flag the driver as engaged with this rider so location auto-forwards
                if driver_id in ACTIVE_DRIVERS:
                    ACTIVE_DRIVERS[driver_id]['assigned_rider_id'] = rider_id
        else:
            socketio.emit('ride_accepted_error', {"error": "Could not assign ride to you."}, room=f"driver_{driver_id}")

@socketio.on('decline_ride')
def handle_decline_ride(data):
    user = get_user_from_token(data.get('token'))
    if not user or user['role'] != 'driver':
        return
        
    ride_id = data.get('rideID')
    driver_id = user['id']
    
    if ride_id in DISPATCH_QUEUE:
        DISPATCH_QUEUE[ride_id]['declined_drivers'].add(driver_id)
