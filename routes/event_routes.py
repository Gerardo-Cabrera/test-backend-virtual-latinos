from flask import Blueprint, request, jsonify
from models import Event, mongo
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson.objectid import ObjectId
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

event_bp = Blueprint('events', __name__)
limiter = Limiter(key_func=get_remote_address)

@event_bp.route('/create', methods=['POST'])
@jwt_required()
@limiter.limit("5 per minute")
def create_event():
    data = request.get_json()
    current_user = get_jwt_identity()
    event = Event(
        title=data['title'],
        description=data['description'],
        date=data['date'],
        time=data['time'],
        location=data['location'],
        price=data['price'],
        organizer_id=current_user
    )
    event.save()
    return jsonify({'message': 'Event created successfully'}), 201

@event_bp.route('/organizer', methods=['GET'])
@jwt_required()
def get_events_for_organizer():
    current_user = get_jwt_identity()
    events = Event.find_by_organizer(current_user)
    events_list = []
    for event in events:
        event['_id'] = str(event['_id'])  # Convert ObjectId to string for JSON serialization
        events_list.append(event)
    return jsonify(events_list), 200

@event_bp.route('/<event_id>', methods=['GET'])
def get_event(event_id):
    event = mongo.db.events.find_one({'_id': ObjectId(event_id)})
    if event:
        event['_id'] = str(event['_id'])  # Convertir ObjectId a string
        return jsonify(event)
    return jsonify({"error": "Event not found"}), 404
