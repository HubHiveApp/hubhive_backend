from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity
from app.database import get_db
from app.models.user import User

# ---------------------------------------------------------------------------
# Decorator: Business account required
# ---------------------------------------------------------------------------
def business_required(fn):
    """
    Route decorator that allows only users with user_type == 'business'.
    """
    @wraps(fn)
    def decorated(*args, **kwargs):
        db       = get_db()
        user_id  = get_jwt_identity()
        user: User = db.query(User).get(user_id)

        if not user or user.user_type != "business":
            return jsonify(error="Business account required"), 403

        return fn(*args, **kwargs)

    return decorated


# ---------------------------------------------------------------------------
# Decorator: Admin required
# ---------------------------------------------------------------------------
def admin_required(fn):
    """
    Route decorator that allows only users with user_type == 'admin'.
    """
    @wraps(fn)
    def decorated(*args, **kwargs):
        db       = get_db()
        user_id  = get_jwt_identity()
        user: User = db.query(User).get(user_id)

        if not user or user.user_type != "admin":
            return jsonify(error="Admin access required"), 403

        return fn(*args, **kwargs)

    return decorated
