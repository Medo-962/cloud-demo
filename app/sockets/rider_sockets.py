from app.__init__ import socketio
from app.sockets.driver_sockets import get_user_from_token

@socketio.on('test_ping')
def handle_ping(data):
    """
    Simple ping to test rider connection.
    """
    user = get_user_from_token(data.get('token'))
    if user and user['role'] == 'rider':
        socketio.emit('test_pong', {"message": "pong from server"}, room=f"rider_{user['id']}")

# More complex logic like cancellation can be added here.
# Driver location updates for a specific ride are handled via broadcasting 
# or explicit emit to rider's room. For example, if driver emits location, 
# dispatch can also ping the rider with the driver's location if the ride is in_progress.
