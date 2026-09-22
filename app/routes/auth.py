from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from app.extensions import db
from app.models import Admin

auth_bp = Blueprint('auth', __name__, url_prefix='/api/v1/auth')

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    admin = Admin.query.filter_by(username=username).first()
    if admin and check_password_hash(admin.password_hash, password):
        access_token = create_access_token(identity=str(admin.id), additional_claims={'role': admin.role})
        return jsonify(access_token=access_token, user={'id': admin.id, 'username': admin.username, 'role': admin.role}), 200
        
    return jsonify({'error': 'Invalid username or password'}), 401
