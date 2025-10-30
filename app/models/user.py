import bcrypt
from sqlalchemy.sql import func
from app.extensions import db

class User(db.Model):
    __tablename__ = "users"

    id       = db.Column(db.Integer, primary_key=True)
    email    = db.Column(db.String(255), unique=True, index=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    username = db.Column(db.String(100), nullable=False)

    bio             = db.Column(db.Text)
    profile_picture = db.Column(db.String(500))
    user_type       = db.Column(db.String(50), default="regular")  # regular|business|admin
    location        = db.Column(db.JSON)
    is_active       = db.Column(db.Boolean, default=True)

    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=func.now())

    # helpers
    def set_password(self, raw):
        self.password = bcrypt.hashpw(raw.encode(), bcrypt.gensalt()).decode()

    def verify_password(self, raw):
        return bcrypt.checkpw(raw.encode(), self.password.encode())

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "username": self.username,
            "bio": self.bio,
            "profile_picture": self.profile_picture,
            "user_type": self.user_type,
            "location": self.location,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
