from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import time

# In-memory storage for MVP
users = []
projects = []
investments = []
messages = []

class User(UserMixin):
    """User model for both farmers and investors."""
    
    def __init__(self, id, username, email, user_type, password, created_at=None):
        self.id = id
        self.username = username
        self.email = email
        self.user_type = user_type  # 'farmer' or 'investor'
        self.password_hash = generate_password_hash(password)
        self.created_at = created_at or time.time()
        self.profile = None
    
    def set_password(self, password):
        """Set password hash for user."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password against hash."""
        return check_password_hash(self.password_hash, password)
    
    def save(self):
        """Save user to in-memory storage."""
        # Check if user already exists
        for i, user in enumerate(users):
            if user.id == self.id:
                users[i] = self
                return self
        # Add new user
        users.append(self)
        return self
    
    @classmethod
    def get_by_id(cls, user_id):
        """Get user by ID."""
        for user in users:
            if user.id == user_id:
                return user
        return None
    
    @classmethod
    def get_by_email(cls, email):
        """Get user by email."""
        for user in users:
            if user.email == email:
                return user
        return None
    
    @classmethod
    def get_by_username(cls, username):
        """Get user by username."""
        for user in users:
            if user.username == username:
                return user
        return None
    
    @classmethod
    def get_all_users(cls):
        """Get all users."""
        return users
    
    @classmethod
    def get_next_id(cls):
        """Get next available user ID."""
        return len(users) + 1


class FarmerProfile:
    """Profile for farmers with farm details."""
    
    def __init__(self, user_id, farm_name, location, size, description, crops=None, technologies=None):
        self.user_id = user_id
        self.farm_name = farm_name
        self.location = location
        self.size = size
        self.description = description
        self.crops = crops or []
        self.technologies = technologies or []
    
    def save(self):
        """Save farmer profile."""
        user = User.get_by_id(self.user_id)
        if user:
            user.profile = self
            return self
        return None


class InvestorProfile:
    """Profile for investors with investment preferences."""
    
    def __init__(self, user_id, company_name=None, investment_focus=None, min_investment=0, 
                 max_investment=0, preferred_locations=None, interests=None):
        self.user_id = user_id
        self.company_name = company_name
        self.investment_focus = investment_focus
        self.min_investment = min_investment
        self.max_investment = max_investment
        self.preferred_locations = preferred_locations or []
        self.interests = interests or []
    
    def save(self):
        """Save investor profile."""
        user = User.get_by_id(self.user_id)
        if user:
            user.profile = self
            return self
        return None


class Project:
    """Project model for farmers seeking investment."""
    
    def __init__(self, id, farmer_id, title, description, funding_goal, 
                 duration, location, category, images=None, created_at=None):
        self.id = id
        self.farmer_id = farmer_id
        self.title = title
        self.description = description
        self.funding_goal = funding_goal
        self.duration = duration
        self.location = location
        self.category = category
        self.images = images or []
        self.created_at = created_at or time.time()
    
    def save(self):
        """Save project to in-memory storage."""
        # Check if project already exists
        for i, project in enumerate(projects):
            if project.id == self.id:
                projects[i] = self
                return self
        # Add new project
        projects.append(self)
        return self
    
    @classmethod
    def get_by_id(cls, project_id):
        """Get project by ID."""
        for project in projects:
            if project.id == project_id:
                return project
        return None
    
    @classmethod
    def get_by_farmer(cls, farmer_id):
        """Get projects by farmer ID."""
        return [p for p in projects if p.farmer_id == farmer_id]
    
    @classmethod
    def get_all_projects(cls):
        """Get all projects."""
        return projects
    
    @classmethod
    def get_next_id(cls):
        """Get next available project ID."""
        return len(projects) + 1


class Investment:
    """Investment model for tracking investments in projects."""
    
    def __init__(self, id, investor_id, project_id, amount, status='pending', created_at=None):
        self.id = id
        self.investor_id = investor_id
        self.project_id = project_id
        self.amount = amount
        self.status = status  # 'pending', 'approved', 'declined'
        self.created_at = created_at or time.time()
    
    def save(self):
        """Save investment to in-memory storage."""
        # Check if investment already exists
        for i, investment in enumerate(investments):
            if investment.id == self.id:
                investments[i] = self
                return self
        # Add new investment
        investments.append(self)
        return self
    
    @classmethod
    def get_by_id(cls, investment_id):
        """Get investment by ID."""
        for investment in investments:
            if investment.id == investment_id:
                return investment
        return None
    
    @classmethod
    def get_by_investor(cls, investor_id):
        """Get investments by investor ID."""
        return [i for i in investments if i.investor_id == investor_id]
    
    @classmethod
    def get_by_project(cls, project_id):
        """Get investments by project ID."""
        return [i for i in investments if i.project_id == project_id]
    
    @classmethod
    def get_all_investments(cls):
        """Get all investments."""
        return investments
    
    @classmethod
    def get_next_id(cls):
        """Get next available investment ID."""
        return len(investments) + 1


class Message:
    """Message model for communication between users."""
    
    def __init__(self, id, sender_id, recipient_id, subject, content, read=False, created_at=None):
        self.id = id
        self.sender_id = sender_id
        self.recipient_id = recipient_id
        self.subject = subject
        self.content = content
        self.read = read
        self.created_at = created_at or time.time()
    
    def save(self):
        """Save message to in-memory storage."""
        # Check if message already exists
        for i, message in enumerate(messages):
            if message.id == self.id:
                messages[i] = self
                return self
        # Add new message
        messages.append(self)
        return self
    
    @classmethod
    def get_by_id(cls, message_id):
        """Get message by ID."""
        for message in messages:
            if message.id == message_id:
                return message
        return None
    
    @classmethod
    def get_by_sender(cls, sender_id):
        """Get messages by sender ID."""
        return [m for m in messages if m.sender_id == sender_id]
    
    @classmethod
    def get_by_recipient(cls, recipient_id):
        """Get messages by recipient ID."""
        return [m for m in messages if m.recipient_id == recipient_id]
    
    @classmethod
    def get_conversation(cls, user1_id, user2_id):
        """Get messages between two users."""
        return [m for m in messages if 
                (m.sender_id == user1_id and m.recipient_id == user2_id) or 
                (m.sender_id == user2_id and m.recipient_id == user1_id)]
    
    @classmethod
    def get_all_messages(cls):
        """Get all messages."""
        return messages
    
    @classmethod
    def get_next_id(cls):
        """Get next available message ID."""
        return len(messages) + 1

# Add sample data for testing
def initialize_sample_data():
    """Initialize sample data for testing."""
    # Sample users (commented out as per guidelines to not include mock data)
    pass
