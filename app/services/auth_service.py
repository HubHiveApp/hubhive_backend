from app.models.user import User
from app.database import get_db
from app.utils.validators import validate_email, validate_password, validate_username
import bcrypt

class AuthService:
    @staticmethod
    def register_user(data):
        db = get_db()
        
        # Validation
        if not validate_email(data.get("email")):
            return None, "Invalid email format"
        if not validate_password(data.get("password")):
            return None, "Password must be at least 8 characters"
        if not validate_username(data.get("username")):
            return None, "Username must be 3-30 alphanumeric characters"
        
        # Check uniqueness
        if db.query(User).filter_by(email=data["email"]).first():
            return None, "Email already registered"
        if db.query(User).filter_by(username=data["username"]).first():
            return None, "Username already taken"
        
        # Create user
        user = User(
            email=data["email"],
            username=data["username"],
            user_type=data.get("user_type", "regular"),
            location=data.get("location", {}),
            bio=data.get("bio", ""),
            profile_picture=data.get("profile_picture")
        )
        user.set_password(data["password"])
        
        db.add(user)
        db.commit()
        
        return user, "User created successfully"

    @staticmethod
    def authenticate_user(email, password):
        db = get_db()
        user = db.query(User).filter_by(email=email).first()
        
        if not user or not user.verify_password(password):
            return None, "Invalid credentials"
        if not user.is_active:
            return None, "Account is deactivated"
            
        return user, "Login successful"

    @staticmethod
    def update_user_profile(user_id, data):
        db = get_db()
        user = db.query(User).get(user_id)
        
        if not user:
            return None, "User not found"
        
        # Update username if provided and unique
        new_username = data.get("username")
        if new_username and new_username != user.username:
            if not validate_username(new_username):
                return None, "Invalid username format"
            if db.query(User).filter(User.username == new_username, User.id != user_id).first():
                return None, "Username already taken"
            user.username = new_username
        
        # Update other fields
        update_fields = ["bio", "location", "profile_picture"]
        for field in update_fields:
            if field in data:
                setattr(user, field, data[field])
        
        db.commit()
        return user, "Profile updated successfully"
