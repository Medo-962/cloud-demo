from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_socketio import SocketIO
from config import Config
from app.models.db import init_db_pool

# Initialize extensions globally
jwt = JWTManager()
socketio = SocketIO(cors_allowed_origins="*")

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize CORS
    CORS(app)

    # Initialize the Database connection pool
    init_db_pool()

    # Initialize JWT
    jwt.init_app(app)

    # Initialize SocketIO
    socketio.init_app(app)

    from app.routes.auth_routes import register_auth_endpoints
    from app.routes.ride_routes import register_ride_endpoints
    from app.routes.user_routes import register_user_endpoints

    register_auth_endpoints(app)
    register_ride_endpoints(app)
    register_user_endpoints(app)

    @app.route('/health', methods=['GET'])
    def health_check():
        return {"status": "healthy"}, 200

    return app
