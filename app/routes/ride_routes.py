import json
from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.ride_service import estimate_price, create_ride_request, get_recent_rides
from app.services.map_service import get_directions_route

def register_ride_endpoints(app):
    @app.route('/api/ride/history', methods=['GET'])
    @jwt_required()
    def history():
        user = json.loads(get_jwt_identity())
        rides, status = get_recent_rides(user['id'], user['role'])
        return jsonify({"history": rides}), status

    @app.route('/api/ride/route', methods=['POST'])
    @jwt_required()
    def route():
        data = request.get_json()
        origin = data.get('origin')
        destination = data.get('destination')
        
        if not origin or not destination:
             return jsonify({"error": "Missing origin or destination"}), 400
             
        route_data = get_directions_route(origin, destination)
        if route_data:
            return jsonify(route_data), 200
        return jsonify({"error": "Could not fetch route details."}), 400

    @app.route('/api/ride/estimate', methods=['POST'])
    @jwt_required()
    def estimate():
        data = request.get_json()
        origin = data.get('origin')
        destination = data.get('destination')
        
        if not origin or not destination:
             return jsonify({"error": "Missing origin or destination"}), 400
             
        response, status_code = estimate_price(origin, destination)
        return jsonify(response), status_code

    @app.route('/api/ride/request', methods=['POST'])
    @jwt_required()
    def request_ride():
        user = json.loads(get_jwt_identity())
        if user['role'] != 'rider':
            return jsonify({"error": "Only riders can request a ride"}), 403
            
        data = request.get_json()
        
        required_fields = ['pickupAddress', 'dropoffAddress', 'pickupLat', 'pickupLng', 'dropoffLat', 'dropoffLng']
        if not all(field in data for field in required_fields):
             return jsonify({"error": "Missing required location data"}), 400
             
        response, status_code = create_ride_request(user['id'], data)
        
        if status_code == 201:
            from app.sockets.dispatch_sockets import dispatch_ride
            dispatch_ride(response['rideID'], data)
            
        return jsonify(response), status_code

