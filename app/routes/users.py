from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.database import get_db
from app.models.user import User

users_bp = Blueprint("users", __name__)

# ---------------------------------------------------------------------------
# Search users
# ---------------------------------------------------------------------------
@users_bp.get("/search")
@jwt_required()
def search_users():
    db = get_db()
    query  = request.args.get("q", "")
    limit  = request.args.get("limit", 10, type=int)

    if len(query) < 2:
        return jsonify(error="Search query must be at least 2 characters"), 400

    users = (
        db.query(User)
        .filter(
            (User.username.ilike(f"%{query}%"))
            | (User.email.ilike(f"%{query}%"))
        )
        .filter(User.is_active.is_(True))
        .limit(limit)
        .all()
    )
    return jsonify(users=[u.to_dict() for u in users]), 200


# ---------------------------------------------------------------------------
# Get user by ID
# ---------------------------------------------------------------------------
@users_bp.get("/<int:user_id>")
@jwt_required()
def get_user(user_id):
    db = get_db()
    user = db.query(User).filter(User.id == user_id, User.is_active.is_(True)).first()
    if not user:
        return jsonify(error="User not found"), 404
    return jsonify(user=user.to_dict()), 200
