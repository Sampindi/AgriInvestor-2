import os
import logging
from flask import Flask
from flask_login import LoginManager

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Create the Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")

# Initialize login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

# Import models after initializing app to avoid circular imports
from models import User

@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login."""
    for user in User.get_all_users():
        if user.id == int(user_id):
            return user
    return None
