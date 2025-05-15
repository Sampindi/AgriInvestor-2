import logging
from app import app, db, socketio

# Set up logging
logger = logging.getLogger(__name__)

# Create tables before importing routes to avoid circular imports
with app.app_context():
    # Import models
    import models
    from models import User
    # Create tables
    db.create_all()
    
    # Check if admin user exists and update if needed
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        # Create new admin user
        admin = User(
            username='admin',
            email='admin@farmlink.com',
            user_type='admin'
        )
        admin.set_password('FarmLink@Admin2025')
        db.session.add(admin)
        db.session.commit()
        logger.info("Admin user created - Username: admin, Email: admin@farmlink.com")
    else:
        # Update existing admin user
        admin.email = 'admin@farmlink.com'
        admin.user_type = 'admin'
        admin.set_password('FarmLink@Admin2025')
        db.session.commit()
        logger.info("Admin user updated - Username: admin, Email: admin@farmlink.com")
    
    logger.info("Database tables created and admin user configured")

# Import routes after tables are created
from routes import *

# Run the app with socketio
if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=True, allow_unsafe_werkzeug=True)
else:
    # For Gunicorn compatibility
    from app import app as application
