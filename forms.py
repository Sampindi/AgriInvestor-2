from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SelectField, FloatField, IntegerField, FileField, SubmitField, SelectMultipleField, BooleanField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, NumberRange, Optional, URL
from models import User

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
        user = User.get_by_username(username.data)
        if user:
            raise ValidationError('That username is already taken. Please choose a different one.')
    
    def validate_email(self, email):
        """Validate that email is unique."""
        user = User.get_by_email(email.data)
        if user:
            raise ValidationError('That email is already registered. Please use a different one or login.')


class FarmerProfileForm(FlaskForm):
    """Form for farmer profile creation/editing."""
    farm_name = StringField('Farm Name', validators=[DataRequired(), Length(max=100)])
    location = StringField('Location (City, State)', validators=[DataRequired(), Length(max=100)])
    size = StringField('Farm Size (acres)', validators=[DataRequired()])
    description = TextAreaField('Farm Description', validators=[DataRequired(), Length(min=10, max=1000)])
    crops = StringField('Crops/Products (comma separated)', validators=[Optional(), Length(max=200)])
    technologies = StringField('Technologies Used (comma separated)', validators=[Optional(), Length(max=200)])
    submit = SubmitField('Save Profile')


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


class InvestmentForm(FlaskForm):
    """Form for making an investment."""
    amount = IntegerField('Investment Amount ($)', validators=[DataRequired(), NumberRange(min=1)])
    submit = SubmitField('Invest')


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
