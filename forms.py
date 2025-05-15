from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, PasswordField, TextAreaField, SelectField, FloatField, IntegerField
from wtforms import SubmitField, SelectMultipleField, BooleanField, RadioField, HiddenField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, NumberRange, Optional, URL
from models import User
from app import db

class LoginForm(FlaskForm):
    """Form for user login."""
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class RegistrationForm(FlaskForm):
    """Form for user registration."""
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    user_type = SelectField('I am a:', choices=[('farmer', 'Farmer'), ('investor', 'Investor')], validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')
    
    def validate_username(self, username):
        """Validate that username is unique."""
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is already taken. Please choose a different one.')
    
    def validate_email(self, email):
        """Validate that email is unique."""
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is already registered. Please use a different one or login.')


class AdminRegistrationForm(FlaskForm):
    """Form for admin registration."""
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    admin_key = PasswordField('Admin Key', validators=[DataRequired()])
    submit = SubmitField('Register as Admin')
    
    def validate_username(self, username):
        """Validate that username is unique."""
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is already taken. Please choose a different one.')
    
    def validate_email(self, email):
        """Validate that email is unique."""
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is already registered. Please use a different one or login.')
    
    def validate_admin_key(self, admin_key):
        """Validate admin key."""
        # In a real application, this would check against a stored or environment key
        # For demonstration, we'll use a simple key
        if admin_key.data != 'aGRbIYB7cV3J9X':
            raise ValidationError('Invalid admin key.')


class FarmerProfileForm(FlaskForm):
    """Form for farmer profile creation/editing."""
    farm_name = StringField('Farm Name', validators=[DataRequired(), Length(max=100)])
    location = StringField('Location (City, State)', validators=[DataRequired(), Length(max=100)])
    size = FloatField('Farm Size (acres)', validators=[DataRequired(), NumberRange(min=0.1)])
    description = TextAreaField('Farm Description', validators=[DataRequired(), Length(min=10, max=1000)])
    crops = StringField('Crops/Products (comma separated)', validators=[Optional(), Length(max=200)])
    technologies = StringField('Technologies Used (comma separated)', validators=[Optional(), Length(max=200)])
    submit = SubmitField('Save Profile')


class FarmImageForm(FlaskForm):
    """Form for uploading farm images."""
    farm_image = FileField('Farm Image', validators=[
        FileRequired(),
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only!')
    ])
    description = StringField('Image Description', validators=[Optional(), Length(max=200)])
    submit = SubmitField('Upload Image')


class InvestorProfileForm(FlaskForm):
    """Form for investor profile creation/editing."""
    company_name = StringField('Company Name (if applicable)', validators=[Optional(), Length(max=100)])
    investment_focus = SelectMultipleField('Investment Focus', 
                                         choices=[
                                             ('sustainable', 'Sustainable Agriculture'),
                                             ('organic', 'Organic Farming'),
                                             ('tech', 'Agricultural Technology'),
                                             ('livestock', 'Livestock'),
                                             ('crops', 'Crop Production'),
                                             ('processing', 'Food Processing'),
                                             ('equipment', 'Farm Equipment'),
                                             ('other', 'Other')
                                         ])
    min_investment = IntegerField('Minimum Investment ($)', validators=[Optional(), NumberRange(min=0)])
    max_investment = IntegerField('Maximum Investment ($)', validators=[Optional(), NumberRange(min=0)])
    preferred_locations = StringField('Preferred Locations (comma separated)', validators=[Optional(), Length(max=200)])
    interests = TextAreaField('Investment Interests', validators=[Optional(), Length(max=500)])
    submit = SubmitField('Save Profile')


class ProjectForm(FlaskForm):
    """Form for creating/editing a project."""
    title = StringField('Project Title', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Project Description', validators=[DataRequired(), Length(min=10, max=2000)])
    funding_goal = IntegerField('Funding Goal ($)', validators=[DataRequired(), NumberRange(min=1)])
    duration = IntegerField('Project Duration (days)', validators=[DataRequired(), NumberRange(min=1, max=365)])
    location = StringField('Project Location', validators=[DataRequired(), Length(max=100)])
    category = SelectField('Project Category', 
                         choices=[
                             ('equipment', 'Farm Equipment'),
                             ('expansion', 'Farm Expansion'),
                             ('technology', 'New Technology'),
                             ('infrastructure', 'Infrastructure'),
                             ('organic', 'Organic Transition'),
                             ('startup', 'Farm Startup'),
                             ('other', 'Other')
                         ], 
                         validators=[DataRequired()])
    submit = SubmitField('Save Project')


class ProjectImageForm(FlaskForm):
    """Form for uploading project images."""
    project_image = FileField('Project Image', validators=[
        FileRequired(),
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only!')
    ])
    description = StringField('Image Description', validators=[Optional(), Length(max=200)])
    submit = SubmitField('Upload Image')


class InvestmentForm(FlaskForm):
    """Form for making an investment."""
    amount = IntegerField('Investment Amount ($)', validators=[DataRequired(), NumberRange(min=1)])
    submit = SubmitField('Invest')


class FarmerRatingForm(FlaskForm):
    """Form for rating farmers."""
    rating = RadioField('Rating', choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')], 
                        validators=[DataRequired()], coerce=int)
    comment = TextAreaField('Comment', validators=[Optional(), Length(max=500)])
    submit = SubmitField('Submit Rating')


class ContactForm(FlaskForm):
    """Form for contact messages."""
    name = StringField('Your Name', validators=[DataRequired(), Length(max=100)])
    email = StringField('Your Email', validators=[DataRequired(), Email()])
    subject = StringField('Subject', validators=[DataRequired(), Length(max=100)])
    message = TextAreaField('Message', validators=[DataRequired(), Length(min=10, max=1000)])
    submit = SubmitField('Send Message')


class MessageForm(FlaskForm):
    """Form for sending messages between users."""
    subject = StringField('Subject', validators=[DataRequired(), Length(max=100)])
    content = TextAreaField('Message', validators=[DataRequired(), Length(min=10, max=1000)])
    submit = SubmitField('Send Message')


class ChatMessageForm(FlaskForm):
    """Form for sending chat messages."""
    content = TextAreaField('Message', validators=[DataRequired(), Length(min=1, max=1000)])
    submit = SubmitField('Send')


class ConnectionRequestForm(FlaskForm):
    """Form for requesting connections."""
    message = TextAreaField('Introduction Message (optional)', validators=[Optional(), Length(max=500)])
    submit = SubmitField('Request Connection')


class SearchForm(FlaskForm):
    """Form for searching projects."""
    query = StringField('Search', validators=[Optional(), Length(max=100)])
    category = SelectField('Category', 
                         choices=[
                             ('', 'All Categories'),
                             ('equipment', 'Farm Equipment'),
                             ('expansion', 'Farm Expansion'),
                             ('technology', 'New Technology'),
                             ('infrastructure', 'Infrastructure'),
                             ('organic', 'Organic Transition'),
                             ('startup', 'Farm Startup'),
                             ('other', 'Other')
                         ], 
                         validators=[Optional()])
    min_funding = IntegerField('Min Funding', validators=[Optional(), NumberRange(min=0)])
    max_funding = IntegerField('Max Funding', validators=[Optional(), NumberRange(min=0)])
    location = StringField('Location', validators=[Optional(), Length(max=100)])
    submit = SubmitField('Search')


class UserSearchForm(FlaskForm):
    """Form for searching users."""
    query = StringField('Search', validators=[Optional(), Length(max=100)])
    user_type = SelectField('User Type', 
                         choices=[
                             ('', 'All Users'),
                             ('farmer', 'Farmers'),
                             ('investor', 'Investors')
                         ], 
                         validators=[Optional()])
    location = StringField('Location', validators=[Optional(), Length(max=100)])
    submit = SubmitField('Search')
