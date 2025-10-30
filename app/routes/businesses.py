from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.database import get_db
from app.models.user     import User
from app.models.chatroom import Chatroom
from app.models.event    import Event

businesses_bp = Blueprint("businesses", __name__)

# ---------------------------------------------------------------------------
# Update business profile
# ---------------------------------------------------------------------------
@businesses_bp.put("/profile")
@jwt_required()
def update_business_profile():
    db = get_db()
    user_id = get_jwt_identity()
    user = db.query(User).get(user_id)

    if not user or user.user_type != "business":
        return jsonify(error="Business account required"), 403

    data = request.get_json() or {}
    for field in ("location", "bio", "profile_picture"):
        if field in data:
            setattr(user, field, data[field])

    db.commit()
    return jsonify(message="Business profile updated", user=user.to_dict()), 200


# ---------------------------------------------------------------------------
# List chatrooms owned by business
# ---------------------------------------------------------------------------
@businesses_bp.get("/my-chatrooms")
@jwt_required()
def get_my_chatrooms():
    db = get_db()
    user_id = get_jwt_identity()
    user = db.query(User).get(user_id)

    if not user or user.user_type != "business":
        return jsonify(error="Business account required"), 403

    rooms = db.query(Chatroom).filter(Chatroom.business_id == user_id).all()
    return jsonify(chatrooms=[r.to_dict() for r in rooms]), 200


# ---------------------------------------------------------------------------
# List events owned by business
# ---------------------------------------------------------------------------
@businesses_bp.get("/my-events")
@jwt_required()
def get_my_events():
    db = get_db()
    user_id = get_jwt_identity()
    user = db.query(User).get(user_id)

    if not user or user.user_type != "business":
        return jsonify(error="Business account required"), 403

    events = db.query(Event).filter(Event.business_id == user_id).all()
    return jsonify(events=[e.to_dict() for e in events]), 200
