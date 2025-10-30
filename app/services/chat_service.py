from app.models.chatroom import Chatroom, chatroom_participants
from app.models.message import Message
from app.models.user import User
from app.database import get_db
from datetime import datetime

class ChatService:
    @staticmethod
    def create_chatroom(user_id, data):
        db = get_db()
        
        if not data.get("name"):
            return None, "Chatroom name is required"
        
        room = Chatroom(
            name=data["name"],
            description=data.get("description", ""),
            business_id=data.get("business_id"),
            location=data.get("location", {}),
            is_private=data.get("is_private", False),
            max_participants=data.get("max_participants", 100),
            created_by=user_id,
        )
        db.add(room)
        db.commit()
        
        # Add creator as participant
        creator = db.query(User).get(user_id)
        room.participants.append(creator)
        db.commit()
        
        return room, "Chatroom created successfully"

    @staticmethod
    def join_chatroom(user_id, room_id):
        db = get_db()
        
        room = db.query(Chatroom).get(room_id)
        if not room:
            return None, "Chatroom not found"
        
        user = db.query(User).get(user_id)
        if user in room.participants:
            return room, "Already in chatroom"
        
        if len(room.participants) >= room.max_participants:
            return None, "Chatroom is full"
        
        room.participants.append(user)
        db.commit()
        
        return room, "Joined chatroom successfully"

    @staticmethod
    def send_message(room_id, user_id, content, message_type="text", media_url=None):
        db = get_db()
        
        room = db.query(Chatroom).get(room_id)
        user = db.query(User).get(user_id)
        
        if not room or not user:
            return None, "Invalid chatroom or user"
        
        if room.is_private and user not in room.participants:
            return None, "Not a participant"
        
        message = Message(
            chatroom_id=room_id,
            user_id=user_id,
            content=content,
            message_type=message_type,
            media_url=media_url,
            created_at=datetime.utcnow(),
        )
        db.add(message)
        db.commit()
        
        return message, "Message sent successfully"

    @staticmethod
    def get_chatroom_messages(room_id, user_id, limit=50, offset=0):
        db = get_db()
        
        room = db.query(Chatroom).get(room_id)
        user = db.query(User).get(user_id)
        
        if not room:
            return None, "Chatroom not found"
        if room.is_private and user not in room.participants:
            return None, "Access denied"
        
        messages = (
            db.query(Message)
            .filter(Message.chatroom_id == room_id)
            .order_by(Message.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )
        
        return list(reversed(messages)), "Messages retrieved successfully"
