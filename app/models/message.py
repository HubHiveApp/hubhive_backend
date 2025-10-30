from sqlalchemy.sql import func
from app.extensions import db

class Message(db.Model):
    __tablename__ = "messages"

    id          = db.Column(db.Integer, primary_key=True)
    chatroom_id = db.Column(db.Integer, db.ForeignKey("chatrooms.id"), nullable=False)
    user_id     = db.Column(db.Integer, db.ForeignKey("users.id"),    nullable=False)
    content     = db.Column(db.Text, nullable=False)

    message_type = db.Column(db.String(50), default="text")
    media_url    = db.Column(db.String(500))
    created_at   = db.Column(db.DateTime(timezone=True), server_default=func.now())

    # relations
    user     = db.relationship("User",     backref="messages")
    chatroom = db.relationship("Chatroom", backref="messages")

    def to_dict(self):
        return {
            "id": self.id,
            "chatroom_id": self.chatroom_id,
            "user_id": self.user_id,
            "content": self.content,
            "message_type": self.message_type,
            "media_url": self.media_url,
            "username": self.user.username if self.user else None,
            "profile_picture": self.user.profile_picture if self.user else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
