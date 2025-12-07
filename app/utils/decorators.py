from functools import wraps
from flask import jsonify, request
from flask_jwt_extended import get_jwt_identity, decode_token
from app.database import get_db
from app.models.user import User
from flask_socketio import emit

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


# ---------------------------------------------------------------------------
# Decorator: Socket.IO JWT required
# ---------------------------------------------------------------------------
def socket_jwt_required(fn):
    """
    Socket.IO event decorator that enforces JWT auth.

    Token sources supported:
    - Event payload dict: first arg `data` contains key `token`
    - Connection query string: `?token=...` (available via `request.args`)
    - For `connect` handlers: pass `auth={ token: "..." }` from client;
      the connect handler should accept the `auth` parameter and forward it
      as the first arg, so this decorator can read it.

    Sets `user` to the authenticated `User` instance and `user_id` to its id
    when calling the wrapped function, via keyword arguments.
    """

    @wraps(fn)
    def decorated(*args, **kwargs):
        db = get_db()

        token = None

        # 1) Try payload dict from first positional arg (for regular events like send_message)
        if args and isinstance(args[0], dict):
            token = args[0].get("token") or args[0].get("access_token")

        # 2) Try connect auth payload - Socket.IO passes auth as a keyword argument
        if token is None and "auth" in kwargs and isinstance(kwargs.get("auth"), dict):
            token = kwargs["auth"].get("token") or kwargs["auth"].get("access_token")

        # 3) Try query string (e.g., ws URL: /socket.io/?token=...)
        if token is None:
            token = request.args.get("token")

        if not token:
            emit("error", {"error": "Unauthorized: missing token"})
            return

        try:
            decoded = decode_token(token)
            user_id = decoded.get("sub") or decoded.get("identity")
        except Exception as e:
            emit("error", {"error": f"Unauthorized: invalid token - {str(e)}"})
            return

        if not user_id:
            emit("error", {"error": "Unauthorized: invalid identity"})
            return

        user: User = db.query(User).get(user_id)
        if not user:
            emit("error", {"error": "Unauthorized: user not found"})
            return

        # Provide user context to handler
        kwargs.setdefault("user_id", user.id)
        kwargs.setdefault("user", user)

        return fn(*args, **kwargs)

    return decorated
