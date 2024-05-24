from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt
from models import mongo, User
from utils.email_utils import send_email
from werkzeug.security import generate_password_hash
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

auth_bp = Blueprint('auth', __name__)
limiter = Limiter(key_func=get_remote_address)

@auth_bp.route('/login', methods=['POST'])
@limiter.limit("10 per minute")
def login():
    data = request.get_json()
    user_data = User.find_by_email(data['email'])
    print(user_data)
    if user_data and User.check_password(user_data['password'], data['password']):
        access_token = create_access_token(identity=str(user_data['_id']))
        return jsonify({'token': access_token}), 200
    return jsonify({'message': 'Invalid credentials'}), 401

@auth_bp.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    return jsonify(message="This is a protected route"), 200

@auth_bp.route('/register', methods=['POST'])
def register():
    user = {
        "name": request.json['username'],
        "email": request.json['email'],
        "password": generate_password_hash(request.json['password'])  # En un entorno real, asegúrate de hashear las contraseñas
    }
    mongo.db.users.insert_one(user)
    return jsonify(message="User added successfully"), 201

@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    data = request.get_json()
    user_data = User.find_by_email(data['email'])
    if user_data:
        new_password = generate_password_hash(data['new_password'])
        mongo.db.users.update_one({'_id': user_data['_id']}, {'$set': {'password': new_password}})
        send_email('Password Reset', [data['email']], 'Your password has been reset.')
        return jsonify({'message': 'Password reset successfully'}), 200
    return jsonify({'message': 'User not found'}), 404

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    jti = get_jwt()["jti"]
    mongo.db.token_blacklist.insert_one({"jti": jti})
    return jsonify(msg="Successfully logged out"), 200
