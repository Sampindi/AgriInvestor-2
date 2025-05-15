import os
import logging
from dotenv import load_dotenv
import eventlet
eventlet.monkey_patch()

from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_socketio import SocketIO
import datetime

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Define base model class
class Base(DeclarativeBase):
    pass

# Initialize extensions
db = SQLAlchemy(model_class=Base)
socketio = SocketIO(cors_allowed_origins="*", async_mode='eventlet')

# Create the Flask app
app = Flask(__name__)

# Configure SQLite database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///farmlink.db"
logger.info("Using SQLite database")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Set secret key
secret_key = os.environ.get("SESSION_SECRET")
if not secret_key:
    # Use a default in development, but log a warning
    secret_key = "dev_secret_key_for_testing_only"
    logger.warning("SESSION_SECRET not found, using a default key (not secure for production)")
app.secret_key = secret_key

logger.info("Initializing Flask application with configurations")

# Initialize extensions with app
db.init_app(app)
socketio.init_app(app)

# Initialize login manager
login_manager = LoginManager()
login_manager.init_app(app)
# Set login view as a string
login_manager.login_view = 'login'  # type: ignore
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

# Create a folder for uploaded files if it doesn't exist
if app.static_folder:
    uploads_dir = os.path.join(app.static_folder, 'uploads')
    if not os.path.exists(uploads_dir):
        os.makedirs(uploads_dir)
        
    # Create a folder for farm images if it doesn't exist
    farm_images_dir = os.path.join(uploads_dir, 'farm_images')
    if not os.path.exists(farm_images_dir):
        os.makedirs(farm_images_dir)

    # Create a folder for project images if it doesn't exist
    project_images_dir = os.path.join(uploads_dir, 'project_images')
    if not os.path.exists(project_images_dir):
        os.makedirs(project_images_dir)

    # Create a folder for static audio if it doesn't exist
    audio_dir = os.path.join(app.static_folder, 'audio')
    if not os.path.exists(audio_dir):
        os.makedirs(audio_dir)
else:
    logger.warning("Static folder is not configured, skipping directory creation")

# Import User model
from models import User

# Setup user_loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login."""
    try:
        return User.query.get(int(user_id))
    except Exception as e:
        logger.error(f"Error loading user: {e}")
        return None

# Add template filter for formatting dates
@app.template_filter('now')
def filter_now(format_string):
    """Return the current date formatted according to format_string."""
    return datetime.datetime.now().strftime(format_string)
