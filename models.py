import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from app import db

# Association tables
user_connections = db.Table('user_connections',
    db.Column('requester_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('receiver_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('status', db.String(20), default='pending'),  # pending, accepted, rejected
    db.Column('created_at', db.DateTime, default=datetime.datetime.utcnow)
)

class User(UserMixin, db.Model):
    """User model for farmers, investors, and admins."""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    user_type = db.Column(db.String(20), nullable=False)  # 'farmer', 'investor', or 'admin'
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relationships
    farmer_profile = db.relationship('FarmerProfile', backref='user', uselist=False, cascade='all, delete-orphan')
    investor_profile = db.relationship('InvestorProfile', backref='user', uselist=False, cascade='all, delete-orphan')
    projects = db.relationship('Project', backref='farmer', lazy='dynamic')
    investments = db.relationship('Investment', backref='investor', lazy='dynamic')
    ratings_given = db.relationship('FarmerRating', backref='rater', foreign_keys='FarmerRating.rater_id', lazy='dynamic')
    ratings_received = db.relationship('FarmerRating', backref='farmer', foreign_keys='FarmerRating.farmer_id', lazy='dynamic')
    
    # Connection relationships
    connections_requested = db.relationship(
        'User', secondary=user_connections,
        primaryjoin=(user_connections.c.requester_id == id),
        secondaryjoin=(user_connections.c.receiver_id == id),
        backref=db.backref('connection_requests', lazy='dynamic'),
        lazy='dynamic'
    )
    
    # Messages
    messages_sent = db.relationship('Message', 
                                 foreign_keys='Message.sender_id',
                                 backref='sender', 
                                 lazy='dynamic')
    messages_received = db.relationship('Message', 
                                     foreign_keys='Message.recipient_id',
                                     backref='recipient', 
                                     lazy='dynamic')
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def set_password(self, password):
        """Set password hash for user."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password against hash."""
        return check_password_hash(self.password_hash, password)
    
    def request_connection(self, user):
        """Request connection with another user."""
        if user.id == self.id:
            return False
        
        # Check if connection already exists
        stmt = user_connections.select().where(
            ((user_connections.c.requester_id == self.id) & 
             (user_connections.c.receiver_id == user.id)) |
            ((user_connections.c.requester_id == user.id) & 
             (user_connections.c.receiver_id == self.id))
        )
        existing = db.session.execute(stmt).first()
        
        if existing is None:
            # Create new connection request
            db.session.execute(
                user_connections.insert().values(
                    requester_id=self.id,
                    receiver_id=user.id,
                    status='pending',
                    created_at=datetime.datetime.utcnow()
                )
            )
            db.session.commit()
            return True
        return False
    
    def accept_connection(self, user):
        """Accept connection request from another user."""
        # Find pending connection request
        stmt = user_connections.select().where(
            (user_connections.c.requester_id == user.id) & 
            (user_connections.c.receiver_id == self.id) &
            (user_connections.c.status == 'pending')
        )
        existing = db.session.execute(stmt).first()
        
        if existing:
            # Update status to accepted
            update_stmt = user_connections.update().where(
                (user_connections.c.requester_id == user.id) & 
                (user_connections.c.receiver_id == self.id)
            ).values(status='accepted')
            db.session.execute(update_stmt)
            db.session.commit()
            return True
        return False
    
    def reject_connection(self, user):
        """Reject connection request from another user."""
        # Find pending connection request
        stmt = user_connections.select().where(
            (user_connections.c.requester_id == user.id) & 
            (user_connections.c.receiver_id == self.id) &
            (user_connections.c.status == 'pending')
        )
        existing = db.session.execute(stmt).first()
        
        if existing:
            # Update status to rejected
            update_stmt = user_connections.update().where(
                (user_connections.c.requester_id == user.id) & 
                (user_connections.c.receiver_id == self.id)
            ).values(status='rejected')
            db.session.execute(update_stmt)
            db.session.commit()
            return True
        return False
    
    def get_connection_status(self, user):
        """Get connection status with another user."""
        stmt1 = user_connections.select().where(
            (user_connections.c.requester_id == self.id) & 
            (user_connections.c.receiver_id == user.id)
        )
        conn1 = db.session.execute(stmt1).first()
        
        if conn1:
            return conn1.status
        
        stmt2 = user_connections.select().where(
            (user_connections.c.requester_id == user.id) & 
            (user_connections.c.receiver_id == self.id)
        )
        conn2 = db.session.execute(stmt2).first()
        
        if conn2:
            return conn2.status
        
        return None
    
    def get_connected_users(self):
        """Get all users connected to this user."""
        stmt1 = user_connections.select().where(
            (user_connections.c.requester_id == self.id) & 
            (user_connections.c.status == 'accepted')
        )
        conn1 = db.session.execute(stmt1).all()
        
        stmt2 = user_connections.select().where(
            (user_connections.c.receiver_id == self.id) & 
            (user_connections.c.status == 'accepted')
        )
        conn2 = db.session.execute(stmt2).all()
        
        connected_ids = [c.receiver_id for c in conn1] + [c.requester_id for c in conn2]
        return User.query.filter(User.id.in_(connected_ids)).all()
    
    def get_pending_connection_requests(self):
        """Get pending connection requests for this user."""
        stmt = user_connections.select().where(
            (user_connections.c.receiver_id == self.id) & 
            (user_connections.c.status == 'pending')
        )
        requests = db.session.execute(stmt).all()
        requester_ids = [r.requester_id for r in requests]
        return User.query.filter(User.id.in_(requester_ids)).all()
    
    def get_avg_rating(self):
        """Get average rating for a farmer."""
        if self.user_type != 'farmer':
            return None
            
        ratings = self.ratings_received.all()
        if not ratings:
            return 0
        return sum(r.rating for r in ratings) / len(ratings)
    
    def is_connected_with(self, user_id):
        """Check if user is connected with another user."""
        return any(u.id == user_id for u in self.get_connected_users())


class FarmerProfile(db.Model):
    """Profile for farmers with farm details."""
    __tablename__ = 'farmer_profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    farm_name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    size = db.Column(db.Float, nullable=False)  # in acres
    description = db.Column(db.Text, nullable=False)
    crops = db.Column(db.String(200))  # Comma separated list
    technologies = db.Column(db.String(200))  # Comma separated list
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Farm images
    images = db.relationship('FarmImage', backref='farmer_profile', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<FarmerProfile {self.farm_name}>'
    
    def get_crops_list(self):
        """Get list of crops from comma-separated string."""
        return [crop.strip() for crop in (self.crops or '').split(',')] if self.crops else []
    
    def get_technologies_list(self):
        """Get list of technologies from comma-separated string."""
        return [tech.strip() for tech in (self.technologies or '').split(',')] if self.technologies else []


class FarmImage(db.Model):
    """Images of farms uploaded by farmers."""
    __tablename__ = 'farm_images'
    
    id = db.Column(db.Integer, primary_key=True)
    profile_id = db.Column(db.Integer, db.ForeignKey('farmer_profiles.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255))
    uploaded_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    
    def __repr__(self):
        return f'<FarmImage {self.filename}>'


class InvestorProfile(db.Model):
    """Profile for investors with investment preferences."""
    __tablename__ = 'investor_profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    company_name = db.Column(db.String(100))
    investment_focus = db.Column(db.String(200))  # Comma separated list
    min_investment = db.Column(db.Integer, default=0)  # in dollars
    max_investment = db.Column(db.Integer, default=0)  # in dollars
    preferred_locations = db.Column(db.String(200))  # Comma separated list
    interests = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    def __repr__(self):
        return f'<InvestorProfile {self.company_name or "Unnamed"}>'
    
    def get_investment_focus_list(self):
        """Get list of investment focus areas from comma-separated string."""
        return [focus.strip() for focus in (self.investment_focus or '').split(',')] if self.investment_focus else []
    
    def get_preferred_locations_list(self):
        """Get list of preferred locations from comma-separated string."""
        return [loc.strip() for loc in (self.preferred_locations or '').split(',')] if self.preferred_locations else []


class Project(db.Model):
    """Project model for farmers seeking investment."""
    __tablename__ = 'projects'
    
    id = db.Column(db.Integer, primary_key=True)
    farmer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    funding_goal = db.Column(db.Integer, nullable=False)  # in dollars
    duration = db.Column(db.Integer, nullable=False)  # in days
    location = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    end_date = db.Column(db.DateTime)
    
    # Relationships
    investments = db.relationship('Investment', backref='project', lazy='dynamic', cascade='all, delete-orphan')
    images = db.relationship('ProjectImage', backref='project', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Project {self.title}>'
    
    @property
    def total_invested(self):
        """Calculate total amount invested in the project."""
        return sum(i.amount for i in self.investments.all())
    
    @property
    def funding_percentage(self):
        """Calculate funding percentage."""
        if self.funding_goal <= 0:
            return 0
        return min(100, int((self.total_invested / self.funding_goal) * 100))
    
    @property
    def days_remaining(self):
        """Calculate days remaining until project end date."""
        if not self.end_date:
            return 0
        delta = self.end_date - datetime.datetime.utcnow()
        return max(0, delta.days)


class ProjectImage(db.Model):
    """Images for projects."""
    __tablename__ = 'project_images'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255))
    uploaded_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    
    def __repr__(self):
        return f'<ProjectImage {self.filename}>'


class Investment(db.Model):
    """Investment model for tracking investments in projects."""
    __tablename__ = 'investments'
    
    id = db.Column(db.Integer, primary_key=True)
    investor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    amount = db.Column(db.Integer, nullable=False)  # in dollars
    status = db.Column(db.String(20), default='pending')  # pending, approved, declined
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    approved_at = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<Investment {self.amount} by {self.investor_id} in {self.project_id}>'


class FarmerRating(db.Model):
    """Ratings given to farmers by investors or admins."""
    __tablename__ = 'farmer_ratings'
    
    id = db.Column(db.Integer, primary_key=True)
    farmer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    rater_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 stars
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    
    __table_args__ = (
        db.UniqueConstraint('farmer_id', 'rater_id', name='unique_farmer_rater'),
    )
    
    def __repr__(self):
        return f'<FarmerRating {self.rating} for {self.farmer_id} by {self.rater_id}>'


class Message(db.Model):
    """Message model for communication between users."""
    __tablename__ = 'messages'
    
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    subject = db.Column(db.String(100))
    content = db.Column(db.Text, nullable=False)
    read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    
    def __repr__(self):
        return f'<Message {self.subject or "No subject"} from {self.sender_id} to {self.recipient_id}>'


class Activity(db.Model):
    """Activity model for tracking system activities for admin dashboard."""
    __tablename__ = 'activities'
    
    id = db.Column(db.Integer, primary_key=True)
    activity_type = db.Column(db.String(50), nullable=False)  # user_registration, new_project, investment, etc.
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    related_user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'))
    investment_id = db.Column(db.Integer, db.ForeignKey('investments.id'))
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    icon = db.Column(db.String(50), default='fa-info-circle')  # Font Awesome icon class
    
    # Relationships
    user = db.relationship('User', foreign_keys=[user_id])
    related_user = db.relationship('User', foreign_keys=[related_user_id])
    project = db.relationship('Project', foreign_keys=[project_id])
    investment = db.relationship('Investment', foreign_keys=[investment_id])
    
    def __repr__(self):
        return f'<Activity {self.activity_type} by {self.user_id} at {self.created_at}>'
    
    @property
    def time_ago(self):
        """Return a human-readable string representing how long ago this activity occurred."""
        now = datetime.datetime.utcnow()
        diff = now - self.created_at
        
        if diff.days > 365:
            years = diff.days // 365
            return f"{years} year{'s' if years != 1 else ''} ago"
        elif diff.days > 30:
            months = diff.days // 30
            return f"{months} month{'s' if months != 1 else ''} ago"
        elif diff.days > 0:
            return f"{diff.days} day{'s' if diff.days != 1 else ''} ago"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} hour{'s' if hours != 1 else ''} ago"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
        else:
            return "Just now"
