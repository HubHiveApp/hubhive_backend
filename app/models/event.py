from sqlalchemy.sql import func
from app.extensions import db

class Event(db.Model):
    __tablename__ = "events"

    id          = db.Column(db.Integer, primary_key=True)
    title       = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    business_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    location    = db.Column(db.JSON)
    event_date  = db.Column(db.DateTime(timezone=True), nullable=False)
    max_attendees = db.Column(db.Integer)
    category    = db.Column(db.String(100))
    is_public   = db.Column(db.Boolean, default=True)
    created_at  = db.Column(db.DateTime(timezone=True), server_default=func.now())

    business = db.relationship("User", backref="events")

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "business_id": self.business_id,
            "business_name": self.business.username if self.business else None,
            "location": self.location,
            "event_date": self.event_date.isoformat() if self.event_date else None,
            "max_attendees": self.max_attendees,
            "category": self.category,
            "is_public": self.is_public,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
