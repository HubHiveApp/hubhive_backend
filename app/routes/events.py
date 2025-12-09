from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.database import get_db
from app.models.event import Event
from app.models.user import User
from datetime import datetime
import math
import logging

events_bp = Blueprint("events", __name__)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Haversine helper
# ---------------------------------------------------------------------------
def _distance_km(lat1, lon1, lat2, lon2):
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )
    return R * (2 * math.atan2(math.sqrt(a), math.sqrt(1 - a)))


# ---------------------------------------------------------------------------
# Create event  (business accounts or admin only)
# ---------------------------------------------------------------------------
@events_bp.post("/")
@jwt_required()
def create_event():
    db = get_db()
    user_id = get_jwt_identity()
    data = request.get_json() or {}

    logger.info("User %s called POST /api/events with data=%s", user_id, data)

    if not data.get("title") or not data.get("event_date"):
        logger.warning(
            "User %s attempted to create event without required fields", user_id
        )
        return jsonify(error="Title and event_date are required"), 400

    user = db.query(User).get(int(user_id))   #to be safe if user is missing and restrict by user_type
    if user.user_type not in ("business", "admin"):
        return jsonify(error="Only business/admin accounts can create events"), 403

    try:
        event_dt = datetime.fromisoformat(
            data["event_date"].replace("Z", "+00:00")
        )
    except ValueError:
        logger.warning(
            "User %s provided invalid event_date format: %s",
            user_id,
            data.get("event_date"),
        )
        return jsonify(error="Invalid event date format"), 400

    event = Event(
        title=data["title"],
        description=data.get("description", ""),
        business_id=user_id,     #busines_id is the *creating* business/admin user
        location=data.get("location", {}),
        event_date=event_dt,
        max_attendees=data.get("max_attendees"),
        category=data.get("category"),
        is_public=data.get("is_public", True),
    )
    db.add(event)
    db.commit()

    logger.info("Event %s created by user %s", event.id, user_id)

    return (
        jsonify(message="Event created successfully", event=event.to_dict()),
        201,
    )


# ---------------------------------------------------------------------------
# List events  (public; optional geo / category filters)
# ---------------------------------------------------------------------------
@events_bp.get("/")
def get_events():
    db = get_db()
    lat = request.args.get("lat", type=float)
    lng = request.args.get("lng", type=float)
    maxd = request.args.get("max_distance", 50, type=float)
    cat = request.args.get("category")

    logger.info(
        "GET /api/events called with lat=%s, lng=%s, max_distance=%s, category=%s",
        lat,
        lng,
        maxd,
        cat,
    )

    query = db.query(Event).filter(Event.is_public.is_(True)).order_by(Event.event_date).filter(Event.event_date >= datetime.utcnow())
    if cat:
        query = query.filter(Event.category == cat)

    events = query.all()
    logger.info("Found %d public events before distance filter", len(events))

    if lat is not None and lng is not None:
        events = [
            e
            for e in events
            if e.location
            and _distance_km(
                lat,
                lng,
                e.location.get("latitude", 0),
                e.location.get("longitude", 0),
            )
            <= maxd
        ]
        logger.info(
            "After distance filter (<= %s km), %d events remain", maxd, len(events)
        )

    return jsonify(events=[e.to_dict() for e in events]), 200


# ---------------------------------------------------------------------------
# Get single event
# ---------------------------------------------------------------------------
@events_bp.get("/<int:event_id>")
def get_event(event_id):
    db = get_db()
    logger.info("GET /api/events/%s called", event_id)

    event = db.query(Event).get(event_id)
    if not event:
        logger.warning("Event %s not found", event_id)
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
    logger.info("User %s called PUT /api/events/%s", user_id, event_id)

    event = db.query(Event).get(event_id)
    if not event:
        logger.warning("User %s tried to update non-existent event %s", user_id, event_id)
        return jsonify(error="Event not found"), 404
    if not (user.user_type == "admin" or event.business_id == user.id):  #this will allow only if this business owns the event or is global admin
        return jsonify(error="Not authorized"), 403


    data = request.get_json() or {}
    logger.info("Updating event %s with data=%s", event_id, data)

    # simple patch update
    for field in (
        "title",
        "description",
        "location",
        "max_attendees",
        "category",
        "is_public",
    ):
        if field in data:
            setattr(event, field, data[field])

    if "event_date" in data:
        try:
            event.event_date = datetime.fromisoformat(
                data["event_date"].replace("Z", "+00:00")
            )
        except ValueError:
            logger.warning(
                "User %s provided invalid event_date format when updating event %s: %s",
                user_id,
                event_id,
                data.get("event_date"),
            )
            return jsonify(error="Invalid event date format"), 400

    db.commit()
    logger.info("Event %s updated successfully by user %s", event_id, user_id)

    return jsonify(message="Event updated", event=event.to_dict()), 200


# ---------------------------------------------------------------------------
# Delete event  (owner only)
# ---------------------------------------------------------------------------
@events_bp.delete("/<int:event_id>")
@jwt_required()
def delete_event(event_id):
    db = get_db()
    user_id = get_jwt_identity()
    logger.info("User %s called DELETE /api/events/%s", user_id, event_id)

    event = db.query(Event).get(event_id)
    if not event:
        logger.warning("User %s tried to delete non-existent event %s", user_id, event_id)
        return jsonify(error="Event not found"), 404
    if not (user.user_type == "admin" or event.business_id == user.id):  #same owner or admin rule as update
        return jsonify(error="Not authorized"), 403

    db.delete(event)
    db.commit()
    logger.info("Event %s deleted by user %s", event_id, user_id)

    return jsonify(message="Event deleted"), 200
