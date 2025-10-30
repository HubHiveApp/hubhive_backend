import os
from app import create_app
from app.extensions import socketio

app = create_app()

if __name__ == "__main__":
    debug = os.getenv("FLASK_DEBUG", "True").lower() == "true"
    socketio.run(
        app, 
        host="0.0.0.0", 
        port=5000, 
        debug=debug, 
        use_reloader=debug
    )
