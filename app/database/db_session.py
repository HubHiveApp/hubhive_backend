"""
Helper so legacy route code can call get_db().
Flask-SQLAlchemy manages the scoped session automatically.
"""
from app.extensions import db
def get_db():
    return db.session
