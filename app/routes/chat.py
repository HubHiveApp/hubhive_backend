from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.database import get_db
from app.models.chatroom import Chatroom
from app.models.message  import Message
from app.models.user     import User
from datetime import datetime
import math

from app.extensions import socketio
from flask_socketio import join_room, leave_room, emit

chat_bp = Blueprint("chat", __name__)

# ---------------------------------------------------------------------------
# Haversine helper
# ---------------------------------------------------------------------------
def _distance_km(lat1, lon1, lat2, lon2):
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) *
         math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) ** 2)
    return R * (2 * math.atan2(math.sqrt(a), math.sqrt(1 - a)))


# ---------------------------------------------------------------------------
# List / discover chatrooms
# ---------------------------------------------------------------------------
@chat_bp.get("/rooms")
@jwt_required()
def get_chatrooms():
    db = get_db()
    lat  = request.args.get("lat", type=float)
    lng  = request.args.get("lng", type=float)
    maxd = request.args.get("max_distance", 10, type=float)

    rooms = db.query(Chatroom).filter(Chatroom.is_private.is_(False)).all()
    if lat and lng:
        rooms = [
            r for r in rooms
            if r.location and
               _distance_km(lat, lng,
                            r.location.get("latitude", 0),
                            r.location.get("longitude", 0)) <= maxd
        ]
    return jsonify(chatrooms=[r.to_dict() for r in rooms]), 200


# ---------------------------------------------------------------------------
# Create chatroom
# ---------------------------------------------------------------------------
@chat_bp.post("/rooms")
@jwt_required()
def create_chatroom():
    db = get_db()
    user_id = get_jwt_identity()
    data = request.get_json() or {}

    if not data.get("name"):
        return jsonify(error="Chatroom name is required"), 400

    room = Chatroom(
        name=data["name"],
        description=data.get("description", ""),
        business_id=data.get("business_id"),
        location=data.get("location", {}),
        is_private=data.get("is_private", False),
        max_participants=data.get("max_participants", 100),
        created_by=user_id,
    )
    db.add(room)
    db.commit()

    # add creator as participant
    creator = db.query(User).get(user_id)
    room.participants.append(creator)
    db.commit()

    return jsonify(message="Chatroom created", chatroom=room.to_dict()), 201


# ---------------------------------------------------------------------------
# Join chatroom
# ---------------------------------------------------------------------------
@chat_bp.post("/rooms/<int:room_id>/join")
@jwt_required()
def join_chatroom(room_id):
    db = get_db()
    user_id = get_jwt_identity()

    room = db.query(Chatroom).get(room_id)
    if not room:
        return jsonify(error="Chatroom not found"), 404

    user = db.query(User).get(user_id)
    if user not in room.participants:
        if len(room.participants) >= room.max_participants:
            return jsonify(error="Chatroom is full"), 400
        room.participants.append(user)
        db.commit()

    return jsonify(message="Joined chatroom", chatroom=room.to_dict()), 200


# ---------------------------------------------------------------------------
# Get messages
# ---------------------------------------------------------------------------
@chat_bp.get("/rooms/<int:room_id>/messages")
@jwt_required()
def get_messages(room_id):
    db = get_db()
    user_id = get_jwt_identity()
    limit  = request.args.get("limit", 50, type=int)
    offset = request.args.get("offset", 0,  type=int)

    room = db.query(Chatroom).get(room_id)
    user = db.query(User).get(user_id)

    if not room:
        return jsonify(error="Chatroom not found"), 404
    if room.is_private and user not in room.participants:
        return jsonify(error="Access denied"), 403

    msgs = (
        db.query(Message)
        .filter(Message.chatroom_id == room_id)
        .order_by(Message.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return jsonify(messages=[m.to_dict() for m in reversed(msgs)]), 200


# ---------------------------------------------------------------------------
# Get single chatroom
# ---------------------------------------------------------------------------
@chat_bp.get("/rooms/<int:room_id>")
@jwt_required()
def get_chatroom(room_id):
    db = get_db()
    user_id = get_jwt_identity()

    room = db.query(Chatroom).get(room_id)
    user = db.query(User).get(user_id)

    if not room:
        return jsonify(error="Chatroom not found"), 404
    if room.is_private and user not in room.participants:
        return jsonify(error="Access denied"), 403
    return jsonify(chatroom=room.to_dict()), 200


# =============================  Socket.IO  ================================= #
@socketio.on("connect")
def _sio_connect():
    print("Client connected")


@socketio.on("disconnect")
def _sio_disconnect():
    print("Client disconnected")


@socketio.on("join_room")
def _sio_join(data):
    room_id = data.get("chatroom_id")
    join_room(str(room_id))
    print("Socket joined room", room_id)


@socketio.on("leave_room")
def _sio_leave(data):
    room_id = data.get("chatroom_id")
    leave_room(str(room_id))
    print("Socket left room", room_id)


@socketio.on("send_message")
def _sio_send(data):
    db = get_db()
    room_id = data.get("chatroom_id")
    user_id = data.get("user_id")
    content = (data.get("content") or "").strip()

    if not content:
        emit("error", {"error": "Message content cannot be empty"})
        return

    room = db.query(Chatroom).get(room_id)
    user = db.query(User).get(user_id)
    if not room or not user:
        emit("error", {"error": "Invalid chatroom or user"})
        return
    if room.is_private and user not in room.participants:
        emit("error", {"error": "Not a participant"})
        return

    msg = Message(
        chatroom_id=room_id,
        user_id=user_id,
        content=content,
        message_type=data.get("message_type", "text"),
        media_url=data.get("media_url"),
        created_at=datetime.utcnow(),
    )
    db.add(msg)
    db.commit()

    emit("new_message", {"message": msg.to_dict()}, room=str(room_id))
