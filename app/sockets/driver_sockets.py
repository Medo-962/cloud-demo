from flask import request
from flask_socketio import emit, join_room, leave_room
from app.__init__ import socketio
from flask_jwt_extended import decode_token

# Store active drivers in memory for quick dispatching
# Dict: {driver_id: {"sid": session_id, "lat": lat, "lng": lng}}
ACTIVE_DRIVERS = {}

def get_user_from_token(token):
    try:
        decoded = decode_token(token)
        return decoded['sub'] # The identity dictionary
    except Exception:
        return None

@socketio.on('connect')
def handle_connect(auth):
    """
    Client should pass auth={'token': 'jwt_here'}
    """
    if not auth or 'token' not in auth:
        return False # Reject connection
        
    user = get_user_from_token(auth['token'])
    if not user:
        return False
        
    room = f"{user['role']}_{user['id']}"
    join_room(room)
    
    if user['role'] == 'driver':
        # Add to tracking dict, wait for location update
        ACTIVE_DRIVERS[user['id']] = {"sid": request.sid, "lat": None, "lng": None}
        print(f"Driver {user['id']} connected. Active drivers: {len(ACTIVE_DRIVERS)}")
    else:
        print(f"Rider {user['id']} connected.")
        
@socketio.on('disconnect')
def handle_disconnect():
    # We would need a reverse lookup to find driver_id by request.sid
    # or require the client to emit an offline event before disconnecting.
    # For now, simplistic loop:
    for driver_id, data in list(ACTIVE_DRIVERS.items()):
        if data['sid'] == request.sid:
            del ACTIVE_DRIVERS[driver_id]
            print(f"Driver {driver_id} disconnected.")
            break

@socketio.on('location_update')
def handle_location_update(data):
    """
    data = {"lat": 24.5, "lng": 46.7, "token": ...}
    Driver emits this every 10 seconds.
    """
    user = get_user_from_token(data.get('token'))
    if not user or user['role'] != 'driver':
        return
        
    driver_id = user['id']
    if driver_id in ACTIVE_DRIVERS:
        ACTIVE_DRIVERS[driver_id]['lat'] = data['lat']
        ACTIVE_DRIVERS[driver_id]['lng'] = data['lng']
        
        # If the driver is currently assigned to a ride, broadcast to the rider
        active_rider_id = ACTIVE_DRIVERS[driver_id].get('assigned_rider_id')
        if active_rider_id:
            socketio.emit('driver_location_update', {
                "driverID": driver_id,
                "lat": data['lat'],
                "lng": data['lng']
            }, room=f"rider_{active_rider_id}")
            
        # We can also update the database asynchronously if required
        # But in-memory is better for rapid dispatch.
