import logging
from app import app, db, socketio

# Set up logging
logger = logging.getLogger(__name__)

# Create tables before importing routes to avoid circular imports
with app.app_context():
    # Import models
    import models
    # Create tables
    db.create_all()
    logger.info("Database tables created")

# Import routes after tables are created
from routes import *

# Run the app with socketio
if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=True, allow_unsafe_werkzeug=True)
else:
    # For Gunicorn compatibility
    from app import app as application
