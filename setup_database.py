#!/usr/bin/env python3
"""
Database setup script for HubHive backend.
Run this script to initialize the database with required tables and sample data.
"""
import os
import sys
from sqlalchemy import create_engine, text

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.chatroom import Chatroom
from app.models.event import Event
import bcrypt

def setup_database():
    """Initialize the database with tables and sample data"""
    app = create_app()
    
    with app.app_context():
        try:
            # Create all tables
            print("Creating database tables...")
            db.create_all()
            print("Tables created successfully")
            
            # Create sample admin user if doesn't exist
            admin_email = "admin@hubhive.com"
            admin_user = User.query.filter_by(email=admin_email).first()
            
            if not admin_user:
                print("Creating sample admin user...")
                admin = User(
                    email=admin_email,
                    username="admin",
                    user_type="admin",
                    bio="System Administrator",
                    location={"latitude": 40.7282, "longitude": -73.7949, "address": "NYU"}
                )
                admin.set_password("admin123")
                db.session.add(admin)
                db.session.commit()
                print("Sample admin user created")
            
            # Create sample business user
            business_email = "coffee@hubhive.com"
            business_user = User.query.filter_by(email=business_email).first()
            
            if not business_user:
                print("Creating sample business user...")
                business = User(
                    email=business_email,
                    username="nyucoffee",
                    user_type="business",
                    bio="Best coffee near NYU!",
                    location={"latitude": 40.7291, "longitude": -73.9965, "address": "123 University Pl"}
                )
                business.set_password("business123")
                db.session.add(business)
                db.session.commit()
                print("Sample business user created")
                
                # Create sample chatroom for the business
                chatroom = Chatroom(
                    name="NYU Coffee Chat",
                    description="Chat with fellow coffee lovers at NYU",
                    business_id=business.id,
                    location=business.location,
                    is_private=False,
                    max_participants=50,
                    created_by=business.id
                )
                db.session.add(chatroom)
                db.session.commit()
                
                # Add business as participant
                chatroom.participants.append(business)
                db.session.commit()
                print("Sample chatroom created")
                
                # Create sample event
                from datetime import datetime, timedelta
                event_date = datetime.utcnow() + timedelta(days=7)
                
                event = Event(
                    title="Coffee Tasting Event",
                    description="Join us for a special coffee tasting session",
                    business_id=business.id,
                    location=business.location,
                    event_date=event_date,
                    max_attendees=20,
                    category="food",
                    is_public=True
                )
                db.session.add(event)
                db.session.commit()
                print("✓ Sample event created")
            
            print("\nDatabase setup completed successfully!")
            print("\nSample accounts:")
            print("  Admin:    admin@hubhive.com / admin123")
            print("  Business: coffee@hubhive.com / business123")
            
        except Exception as e:
            print(f"Error setting up database: {str(e)}")
            db.session.rollback()
            raise

if __name__ == "__main__":
    setup_database()
