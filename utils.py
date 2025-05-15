import re
import datetime
from models import User, Project, FarmerProfile, InvestorProfile
from recommendation_engine import RecommendationEngine

def is_valid_email(email):
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def format_currency(amount):
    """Format a number as currency."""
    return f"${amount:,.2f}"

def format_date(date_obj):
    """Format a datetime object as a readable date."""
    if isinstance(date_obj, (int, float)):
        # Convert timestamp to datetime
        date_obj = datetime.datetime.fromtimestamp(date_obj)
    
    if isinstance(date_obj, datetime.datetime):
        return date_obj.strftime("%B %d, %Y")
    
    return str(date_obj)

def parse_comma_separated(text):
    """Parse a comma-separated string into a list."""
    if not text:
        return []
    return [item.strip() for item in text.split(',') if item.strip()]

def get_unread_message_count(user):
    """Get count of unread messages for a user."""
    if not user.is_authenticated:
        return 0
    
    from models import Message
    return Message.query.filter_by(recipient_id=user.id, read=False).count()

def allowed_file(filename, allowed_extensions=None):
    """Check if a file has an allowed extension."""
    if allowed_extensions is None:
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
    
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

def truncate_text(text, max_length=100):
    """Truncate text to the specified length."""
    if not text or len(text) <= max_length:
        return text
    return text[:max_length] + '...'


def record_activity(db, socketio, activity_type, title, description, user_id=None, related_user_id=None, 
                   project_id=None, investment_id=None, icon=None):
    """
    Record a system activity and emit it to admin users via SocketIO.
    
    Parameters:
    - db: SQLAlchemy database instance
    - socketio: Flask-SocketIO instance
    - activity_type: Type of activity (e.g., 'user_registration', 'new_project', 'investment')
    - title: Title for the activity
    - description: Description of the activity
    - user_id: ID of the primary user involved (optional)
    - related_user_id: ID of a secondary user involved (optional)
    - project_id: ID of related project (optional)
    - investment_id: ID of related investment (optional)
    - icon: Font Awesome icon class (optional)
    """
    from models import Activity
    
    # Set default icon based on activity type if not provided
    if not icon:
        icon_map = {
            'user_registration': 'fa-user-plus',
            'new_project': 'fa-project-diagram',
            'investment': 'fa-dollar-sign',
            'profile_update': 'fa-user-edit',
            'message': 'fa-envelope',
            'connection': 'fa-handshake',
            'rating': 'fa-star'
        }
        icon = icon_map.get(activity_type, 'fa-info-circle')
    
    # Create and save the activity
    activity = Activity(
        activity_type=activity_type,
        user_id=user_id,
        related_user_id=related_user_id,
        project_id=project_id,
        investment_id=investment_id,
        title=title,
        description=description,
        icon=icon
    )
    
    db.session.add(activity)
    db.session.commit()
    
    # We're using polling instead of WebSockets for better reliability
    # Activities will be retrieved via regular HTTP requests
