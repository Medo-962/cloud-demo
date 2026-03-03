import json
from flask import request, jsonify
from flask_jwt_extended import create_access_token
from app.services.auth_service import register_user, authenticate_user

def register_auth_endpoints(app):
    @app.route('/api/auth/register', methods=['POST'])
    def register():
        data = request.get_json()
        role = data.get('role')
        
        if role not in ['rider', 'driver']:
            return jsonify({"error": "Role must be 'rider' or 'driver'"}), 400
            
        response, status_code = register_user(role, data)
        return jsonify(response), status_code

    @app.route('/api/auth/login', methods=['POST'])
    def login():
        data = request.get_json()
        role = data.get('role')
        email = data.get('email')
        password = data.get('password')
        
        if not all([role, email, password]):
            return jsonify({"error": "Missing role, email, or password"}), 400
            
        user_info, status_code = authenticate_user(role, email, password)
        
        if status_code == 200:
            access_token = create_access_token(identity=json.dumps({'id': user_info['id'], 'role': user_info['role']}))
            return jsonify({
                "message": "Login successful",
                "access_token": access_token,
                "user": user_info
            }), 200
        else:
            return jsonify(user_info), status_code

