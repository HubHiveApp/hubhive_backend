# app/routes/auth.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity,
)
from app.database import get_db            # <— clean import via __init__.py
from app.models.user import User
from app.utils.validators import validate_email, validate_password

auth_bp = Blueprint("auth", __name__)


# ---------------------------------------------------------------------------
# Register
# ---------------------------------------------------------------------------
@auth_bp.post("/register")
def register():
    db = get_db()                          # Flask-SQLAlchemy scoped session
    data = request.get_json() or {}

    # basic validation
    if not validate_email(data.get("email")):
        return jsonify(error="Invalid email format"), 400
    if not validate_password(data.get("password")):
        return jsonify(error="Password must be at least 8 characters"), 400
    if not data.get("username"):
        return jsonify(error="Username is required"), 400

    # uniqueness checks
    if db.query(User).filter_by(email=data["email"]).first():
        return jsonify(error="Email already registered"), 400
    if db.query(User).filter_by(username=data["username"]).first():
        return jsonify(error="Username already taken"), 400

    # create user
    user = User(
        email=data["email"],
        username=data["username"],
        user_type=data.get("user_type", "regular"),
        location=data.get("location", {}),
        bio=data.get("bio", ""),
    )
    user.set_password(data["password"])

    db.add(user)
    db.commit()

    access_token = create_access_token(identity=str(user.id))
    return (
        jsonify(message="User created successfully",
                access_token=access_token,
                user=user.to_dict()),
        201,
    )


# ---------------------------------------------------------------------------
# Login
# ---------------------------------------------------------------------------
@auth_bp.post("/login")
def login():
    db = get_db()
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify(error="Email and password are required"), 400

    user = db.query(User).filter_by(email=email).first()
    if not user or not user.verify_password(password):
        return jsonify(error="Invalid credentials"), 401
    if not user.is_active:
        return jsonify(error="Account is deactivated"), 403

    access_token = create_access_token(identity=str(user.id))
    return jsonify(
        message="Login successful",
        access_token=access_token,
        user=user.to_dict(),
    ), 200


# ---------------------------------------------------------------------------
# Get current profile
# ---------------------------------------------------------------------------
@auth_bp.get("/profile")
@jwt_required()
def get_profile():
    db = get_db()
    user_id = get_jwt_identity()
    user = db.query(User).get(int(user_id))
    if not user:
        return jsonify(error="User not found"), 404
    return jsonify(user=user.to_dict()), 200


# ---------------------------------------------------------------------------
# Update profile
# ---------------------------------------------------------------------------
@auth_bp.put("/profile")
@jwt_required()
def update_profile():
    db = get_db()
    user_id = get_jwt_identity()
    user = db.query(User).get(int(user_id))
    if not user:
        return jsonify(error="User not found"), 404

    data = request.get_json() or {}

    # enforce unique username if changed
    new_username = data.get("username")
    if new_username and new_username != user.username:
        if db.query(User).filter(User.username == new_username,
                                 User.id != user_id).first():
            return jsonify(error="Username already taken"), 400
        user.username = new_username

    # optional fields
    if "bio" in data:
        user.bio = data["bio"]
    if "location" in data:
        user.location = data["location"]
    if "profile_picture" in data:
        user.profile_picture = data["profile_picture"]

    db.commit()
    return jsonify(message="Profile updated successfully", user=user.to_dict()), 200
