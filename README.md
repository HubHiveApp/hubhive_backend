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

- **Backend**: Python 3.10+, Flask 2.3.3
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Real-time**: Flask-SocketIO 5.3.6
- **Authentication**: JWT with Flask-JWT-Extended
- **API Documentation**: OpenAPI/Swagger (TBD)
- **Payments**: Stripe API integration
- **Migrations**: Flask-Migrate with Alembic

## How to Run

1. Install and install PostgreSQL and set up a database with username `hubhive_user` and password `password`. [This](https://www.docker.com/blog/how-to-use-the-postgres-docker-official-image/) is a good guide if you haven't done this before, assuming Docker is installed.
1. Create a virtual environment.

    `python -m venv .venv`
2. Activate virtual environment.

    `source .venv/bin/activate`
1. Install packages.

    `pip install -r requirements.txt`
1. Run the setup database script (first time only).

    `python setup_database.py`
1. Start the actual backend.

    `python run.py`

By default, the backend runs on port 8000.

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
