from sqlalchemy.sql import func
from app.extensions import db

chatroom_participants = db.Table(
    "chatroom_participants",
    db.Column("user_id",     db.Integer, db.ForeignKey("users.id")),
    db.Column("chatroom_id", db.Integer, db.ForeignKey("chatrooms.id")),
)

class Chatroom(db.Model):
    __tablename__ = "chatrooms"

    id    = db.Column(db.Integer, primary_key=True)
    name  = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    business_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    location    = db.Column(db.JSON)
    is_private  = db.Column(db.Boolean, default=False)
    max_participants = db.Column(db.Integer, default=100)
    created_by  = db.Column(db.Integer, db.ForeignKey("users.id"))
    created_at  = db.Column(db.DateTime(timezone=True), server_default=func.now())

    # relations
    participants = db.relationship("User", secondary=chatroom_participants, backref="chatrooms")
    business     = db.relationship("User", foreign_keys=[business_id])
    creator      = db.relationship("User", foreign_keys=[created_by])

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "business_id": self.business_id,
            "business_name": self.business.username if self.business else None,
            "location": self.location,
            "is_private": self.is_private,
            "max_participants": self.max_participants,
            "participant_count": len(self.participants),
            "created_by": self.created_by,
            "creator_name": self.creator.username if self.creator else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
