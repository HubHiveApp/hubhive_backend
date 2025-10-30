from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.database import get_db
from app.models.event import Event
from app.models.user  import User
from datetime import datetime
import math

events_bp = Blueprint("events", __name__)

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
# Create event  (business accounts only)
# ---------------------------------------------------------------------------
@events_bp.post("/")
@jwt_required()
def create_event():
    db = get_db()
    user_id = get_jwt_identity()
    data = request.get_json() or {}

    if not data.get("title") or not data.get("event_date"):
        return jsonify(error="Title and event_date are required"), 400

    user = db.query(User).get(user_id)
    if user.user_type != "business":
        return jsonify(error="Only business accounts can create events"), 403

    try:
        event_dt = datetime.fromisoformat(data["event_date"].replace("Z", "+00:00"))
    except ValueError:
        return jsonify(error="Invalid event date format"), 400

    event = Event(
        title=data["title"],
        description=data.get("description", ""),
        business_id=user_id,
        location=data.get("location", {}),
        event_date=event_dt,
        max_attendees=data.get("max_attendees"),
        category=data.get("category"),
        is_public=data.get("is_public", True),
    )
    db.add(event)
    db.commit()
    return jsonify(message="Event created successfully", event=event.to_dict()), 201


# ---------------------------------------------------------------------------
# List events  (public; optional geo / category filters)
# ---------------------------------------------------------------------------
@events_bp.get("/")
def get_events():
    db = get_db()
    lat  = request.args.get("lat",  type=float)
    lng  = request.args.get("lng",  type=float)
    maxd = request.args.get("max_distance", 50, type=float)
    cat  = request.args.get("category")

    query = db.query(Event).filter(Event.is_public.is_(True))
    if cat:
        query = query.filter(Event.category == cat)

    events = query.all()
    if lat and lng:
        events = [
            e for e in events
            if e.location and
               _distance_km(lat, lng,
                            e.location.get("latitude", 0),
                            e.location.get("longitude", 0)) <= maxd
        ]
    return jsonify(events=[e.to_dict() for e in events]), 200


# ---------------------------------------------------------------------------
# Get single event
# ---------------------------------------------------------------------------
@events_bp.get("/<int:event_id>")
def get_event(event_id):
    db = get_db()
    event = db.query(Event).get(event_id)
    if not event:
        return jsonify(error="Event not found"), 404
    return jsonify(event=event.to_dict()), 200


# ---------------------------------------------------------------------------
# Update event  (owner only)
# ---------------------------------------------------------------------------
@events_bp.put("/<int:event_id>")
@jwt_required()
def update_event(event_id):
    db = get_db()
    user_id = get_jwt_identity()
    event = db.query(Event).get(event_id)
    if not event:
        return jsonify(error="Event not found"), 404
    if event.business_id != user_id:
        return jsonify(error="Not authorized"), 403

    data = request.get_json() or {}
    # simple patch update
    for field in (
        "title", "description", "location",
        "max_attendees", "category", "is_public"
    ):
        if field in data:
            setattr(event, field, data[field])

    if "event_date" in data:
        try:
            event.event_date = datetime.fromisoformat(data["event_date"].replace("Z", "+00:00"))
        except ValueError:
            return jsonify(error="Invalid event date format"), 400

    db.commit()
    return jsonify(message="Event updated", event=event.to_dict()), 200


# ---------------------------------------------------------------------------
# Delete event  (owner only)
# ---------------------------------------------------------------------------
@events_bp.delete("/<int:event_id>")
@jwt_required()
def delete_event(event_id):
    db = get_db()
    user_id = get_jwt_identity()
    event = db.query(Event).get(event_id)
    if not event:
        return jsonify(error="Event not found"), 404
    if event.business_id != user_id:
        return jsonify(error="Not authorized"), 403

    db.delete(event)
    db.commit()
    return jsonify(message="Event deleted"), 200
