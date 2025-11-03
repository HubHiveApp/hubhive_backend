# HubHive Backend

A Python-based backend for the HubHive social networking application, providing real-time chat, event management, and location-based services for connecting local communities.

## Features

- **User Management**: Registration, authentication, and profile management
- **Real-time Chat**: Socket.io powered chatrooms with location-based discovery
- **Event Management**: Create, discover, and manage local events
- **Business Accounts**: Special privileges for business owners
- **Location Services**: Geo-based chatroom and event discovery
- **Payment Integration**: Stripe integration for premium features
- **RESTful APIs**: Well-structured API endpoints
- **Database Migrations**: Alembic-based schema management

## Tech Stack

- **Backend**: Python 3.8+, Flask 2.3.3
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Real-time**: Flask-SocketIO 5.3.6
- **Authentication**: JWT with Flask-JWT-Extended
- **API Documentation**: OpenAPI/Swagger (TBD)
- **Payments**: Stripe API integration
- **Migrations**: Flask-Migrate with Alembic

## Project Structure
```tree
hubhive-backend/
├── app/
│ ├── models/ # Database models
│ ├── routes/ # API route handlers
│ ├── services/ # Business logic layer
│ ├── utils/ # Utilities and helpers
│ ├── database/ # Database configuration
│ ├── migrations/ # Database migrations
│ └── static/ # Static files
├── requirements.txt
├── run.py
├── setup_database.py # Database initialization
└── .env.example
```
