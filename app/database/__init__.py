"""
Database package initializer.

We just re-export `get_db` so other modules can do
    from app.database import get_db
instead of reaching into app.database.db_session.
"""

from .db_session import get_db   # noqa: F401
