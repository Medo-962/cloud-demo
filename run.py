import eventlet
eventlet.monkey_patch()

from app.__init__ import create_app, socketio

# Ensure sockets are imported and registered
import app.sockets

app = create_app()

if __name__ == '__main__':
    print("Starting RubbleCab Backend Server on port 5000...")
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, use_reloader=False)
