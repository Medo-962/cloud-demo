import json
from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.user_service import get_user_profile

def register_user_endpoints(app):
    @app.route('/api/user/profile', methods=['GET'])
    @jwt_required()
    def profile():
        user = json.loads(get_jwt_identity())
        profile_data, status_code = get_user_profile(user['id'], user['role'])
        return jsonify(profile_data), status_code

