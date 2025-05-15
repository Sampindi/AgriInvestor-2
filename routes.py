import os
import datetime
from flask import render_template, url_for, flash, redirect, request, session, abort, current_app
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.utils import secure_filename
from app import app, db, socketio
from sqlalchemy import func
from models import User, FarmerProfile, InvestorProfile, Project, Investment, Message, FarmImage, ProjectImage, FarmerRating
from forms import (
    LoginForm, RegistrationForm, FarmerProfileForm, 
    InvestorProfileForm, ProjectForm, InvestmentForm, ContactForm, MessageForm, 
    SearchForm
)
from utils import parse_comma_separated, format_currency, format_date
from recommendation_engine import RecommendationEngine
import logging

logger = logging.getLogger(__name__)

# Name of the app
APP_NAME = "AgriBridge"

@app.route('/')
def index():
    """Homepage route."""
    # Get featured projects (limit to 6)
    try:
        featured_projects = Project.query.order_by(Project.created_at.desc()).limit(6).all()
    except Exception as e:
        logger.error(f"Error retrieving projects: {e}")
        featured_projects = []

    return render_template('index.html', 
                          title='Home', 
                          app_name=APP_NAME,
                          projects=featured_projects)

@app.route('/about')
def about():
    """About page route."""
    try:
        return render_template('about.html', title='About Us', app_name=APP_NAME)
    except Exception as e:
        logger.error(f"Error displaying about page: {e}")
        return "Unable to display About page due to a server error. Please try again later.", 500

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login route."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    form = LoginForm()
    if form.validate_on_submit():
        if form.email.data == 'admin@example.com' and form.password.data == 'AdminPass123!':
            # Hardcoded admin login
            admin = User.query.filter_by(email='admin@example.com').first()
            if admin:
                login_user(admin)
                admin.last_login = datetime.datetime.utcnow()
                db.session.commit()
                flash('Admin login successful!', 'success')
                return redirect(url_for('dashboard'))

        # Regular user login
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            # Update last login time
            user.last_login = datetime.datetime.utcnow()
            db.session.commit()

            login_user(user)
            flash('Login successful!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard'))
        else:
            flash('Login unsuccessful. Please check email and password.', 'danger')

    return render_template('login.html', title='Login', app_name=APP_NAME, form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration route."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            user = User(
                username=form.username.data,
                email=form.email.data,
                user_type=form.user_type.data
            )
            user.set_password(form.password.data)

            db.session.add(user)
            db.session.commit()

            flash(f'Account created successfully! You can now log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error registering user: {e}")
            flash('An error occurred during registration. Please try again.', 'danger')

    return render_template('register.html', title='Register', app_name=APP_NAME, form=form)

# Admin routes removed in favor of hardcoded admin credentials

@app.route('/logout')
def logout():
    """User logout route."""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    """User dashboard route."""
    if current_user.user_type == 'farmer':
        # Get farmer's projects
        projects = current_user.projects.all()

        # Get connection requests
        connection_requests = current_user.get_pending_connection_requests()

        # Get connected investors
        connected_users = current_user.get_connected_users()
        connected_investors = [u for u in connected_users if u.user_type == 'investor']

        # Get similar farms using the recommendation engine
        similar_farms = []
        if current_user.farmer_profile:
            similar_farms = RecommendationEngine.get_similar_farms(current_user.id)

        # Get credibility score
        credibility_score = RecommendationEngine.get_farmer_credibility_score(current_user.id)

        # Get recommended investors
        recommended_investors = RecommendationEngine.recommend_investors_to_farmer(current_user.id)

        return render_template('dashboard.html', 
                              title='Farmer Dashboard', 
                              app_name=APP_NAME,
                              projects=projects,
                              connection_requests=connection_requests,
                              connected_investors=connected_investors,
                              similar_farms=similar_farms,
                              credibility_score=credibility_score,
                              recommended_investors=recommended_investors)

    elif current_user.user_type == 'investor':
        # Get investor's investments
        investments = current_user.investments.all()

        # Get connected farmers
        connected_users = current_user.get_connected_users()
        connected_farmers = [u for u in connected_users if u.user_type == 'farmer']

        # Get recommended projects using the recommendation engine
        recommended_projects = RecommendationEngine.recommend_projects_to_investor(current_user.id)

        return render_template('dashboard.html', 
                              title='Investor Dashboard', 
                              app_name=APP_NAME,
                              investments=investments,
                              connected_farmers=connected_farmers,
                              recommended_projects=recommended_projects)

    else:  # admin
        try:
            # Admin dashboard - show stats and management options
            users = User.query.all()
            projects = Project.query.all()
            farmers = User.query.filter_by(user_type='farmer').all()
            investors = User.query.filter_by(user_type='investor').all()

            # Calculate total funding requested across all projects
            total_funding_requested = db.session.query(func.sum(Project.funding_goal)).scalar() or 0

            # Calculate total funding received across all investments
            total_funding_received = db.session.query(func.sum(Investment.amount)).scalar() or 0

            # Get recent users
            recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()

            # Get recent projects
            recent_projects = Project.query.order_by(Project.created_at.desc()).limit(5).all()

            return render_template('dashboard.html', 
                                title='Admin Dashboard', 
                                app_name=APP_NAME,
                                users=users,
                                projects=projects,
                                farmers=farmers,
                                investors=investors,
                                total_funding_requested=total_funding_requested,
                                total_funding_received=total_funding_received,
                                recent_users=recent_users,
                                recent_projects=recent_projects)
        except Exception as e:
            logger.error(f"Error loading admin dashboard: {e}")
            flash("An error occurred while loading the admin dashboard. Please try again.", "danger")
            return render_template('dashboard.html', 
                                title='Admin Dashboard', 
                                app_name=APP_NAME)

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """User profile route."""
    if current_user.user_type == 'farmer':
        form = FarmerProfileForm()

        if form.validate_on_submit():
            # Check if profile already exists
            if current_user.farmer_profile:
                profile = current_user.farmer_profile
                profile.farm_name = form.farm_name.data
                profile.location = form.location.data
                profile.size = float(form.size.data)
                profile.description = form.description.data
                profile.crops = form.crops.data
                profile.technologies = form.technologies.data
                profile.updated_at = datetime.datetime.utcnow()
            else:
                profile = FarmerProfile(
                    user_id=current_user.id,
                    farm_name=form.farm_name.data,
                    location=form.location.data,
                    size=float(form.size.data),
                    description=form.description.data,
                    crops=form.crops.data,
                    technologies=form.technologies.data
                )
                db.session.add(profile)

            db.session.commit()
            flash('Your farmer profile has been updated!', 'success')
            return redirect(url_for('dashboard'))

        # Pre-fill form if profile exists
        elif request.method == 'GET' and current_user.farmer_profile:
            profile = current_user.farmer_profile
            form.farm_name.data = profile.farm_name
            form.location.data = profile.location
            form.size.data = profile.size
            form.description.data = profile.description
            form.crops.data = profile.crops
            form.technologies.data = profile.technologies

        # Get farm images if they exist
        farm_images = []
        if current_user.farmer_profile:
            farm_images = current_user.farmer_profile.images.all()

        # Get farmer ratings
        ratings = current_user.ratings_received.all()
        avg_rating = current_user.get_avg_rating()

        return render_template('farmer_profile.html', 
                              title='Farmer Profile', 
                              app_name=APP_NAME,
                              form=form,
                              farm_images=farm_images,
                              ratings=ratings,
                              avg_rating=avg_rating)

    else:  # investor
        form = InvestorProfileForm()

        if form.validate_on_submit():
            # Convert form.investment_focus from list to comma-separated string
            investment_focus = ','.join(form.investment_focus.data) if form.investment_focus.data else ''

            # Check if profile already exists
            if current_user.investor_profile:
                profile = current_user.investor_profile
                profile.company_name = form.company_name.data
                profile.investment_focus = investment_focus
                profile.min_investment = form.min_investment.data or 0
                profile.max_investment = form.max_investment.data or 0
                profile.preferred_locations = form.preferred_locations.data
                profile.interests = form.interests.data
                profile.updated_at = datetime.datetime.utcnow()
            else:
                profile = InvestorProfile(
                    user_id=current_user.id,
                    company_name=form.company_name.data,
                    investment_focus=investment_focus,
                    min_investment=form.min_investment.data or 0,
                    max_investment=form.max_investment.data or 0,
                    preferred_locations=form.preferred_locations.data,
                    interests=form.interests.data
                )
                db.session.add(profile)

            db.session.commit()
            flash('Your investor profile has been updated!', 'success')
            return redirect(url_for('dashboard'))

        # Pre-fill form if profile exists
        elif request.method == 'GET' and current_user.investor_profile:
            profile = current_user.investor_profile
            form.company_name.data = profile.company_name

            # Convert comma-separated string to list for investment_focus
            if profile.investment_focus:
                form.investment_focus.data = profile.investment_focus.split(',')

            form.min_investment.data = profile.min_investment
            form.max_investment.data = profile.max_investment
            form.preferred_locations.data = profile.preferred_locations
            form.interests.data = profile.interests

        return render_template('investor_profile.html', 
                              title='Investor Profile', 
                              app_name=APP_NAME,
                              form=form)

@app.route('/upload_farm_image', methods=['POST'])
@login_required
def upload_farm_image():
    """Upload farm image for farmer profile."""
    if current_user.user_type != 'farmer':
        flash('Only farmers can upload farm images.', 'danger')
        return redirect(url_for('profile'))

    if not current_user.farmer_profile:
        flash('Please create your farmer profile first.', 'warning')
        return redirect(url_for('profile'))

    # Check if the post request has the file part
    if 'farm_image' not in request.files:
        flash('No file part', 'danger')
        return redirect(url_for('profile'))

    file = request.files['farm_image']
    if file.filename == '':
        flash('No selected file', 'danger')
        return redirect(url_for('profile'))

    if file:
        # Secure the filename and save the file
        filename = secure_filename(file.filename)
        # Add timestamp to filename to avoid duplicates
        timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        unique_filename = f"{timestamp}_{filename}"

        # Save the file
        file_path = os.path.join(app.static_folder, 'uploads', 'farm_images', unique_filename)
        file.save(file_path)

        # Create farm image record
        image = FarmImage(
            profile_id=current_user.farmer_profile.id,
            filename=unique_filename,
            description=request.form.get('description', '')
        )

        db.session.add(image)
        db.session.commit()

        flash('Farm image uploaded successfully!', 'success')

    return redirect(url_for('profile'))

@app.route('/delete_farm_image/<int:image_id>', methods=['POST'])
@login_required
def delete_farm_image(image_id):
    """Delete farm image."""
    if current_user.user_type != 'farmer':
        flash('Only farmers can delete farm images.', 'danger')
        return redirect(url_for('profile'))

    image = FarmImage.query.get_or_404(image_id)

    # Ensure the image belongs to the current user
    if image.farmer_profile.user_id != current_user.id:
        flash('You do not have permission to delete this image.', 'danger')
        return redirect(url_for('profile'))

    # Delete the file from the filesystem
    file_path = os.path.join(app.static_folder, 'uploads', 'farm_images', image.filename)
    if os.path.exists(file_path):
        os.remove(file_path)

    # Delete the record from the database
    db.session.delete(image)
    db.session.commit()

    flash('Farm image deleted successfully!', 'success')
    return redirect(url_for('profile'))

@app.route('/rate_farmer/<int:farmer_id>', methods=['POST'])
@login_required
def rate_farmer(farmer_id):
    """Rate a farmer (only investors and admins can rate)."""
    if current_user.user_type not in ['investor', 'admin']:
        flash('Only investors and admins can rate farmers.', 'danger')
        return redirect(url_for('index'))

    farmer = User.query.get_or_404(farmer_id)
    if farmer.user_type != 'farmer':
        flash('You can only rate farmers.', 'danger')
        return redirect(url_for('index'))

    # Get rating from form
    rating = request.form.get('rating', type=int)
    comment = request.form.get('comment', '')

    if not rating or rating < 1 or rating > 5:
        flash('Please provide a valid rating (1-5).', 'danger')
        return redirect(url_for('index'))

    # Check if user has already rated this farmer
    existing_rating = FarmerRating.query.filter_by(
        farmer_id=farmer_id, 
        rater_id=current_user.id
    ).first()

    if existing_rating:
        # Update existing rating
        existing_rating.rating = rating
        existing_rating.comment = comment
    else:
        # Create new rating
        new_rating = FarmerRating(
            farmer_id=farmer_id,
            rater_id=current_user.id,
            rating=rating,
            comment=comment
        )
        db.session.add(new_rating)

    db.session.commit()
    flash('Rating submitted successfully!', 'success')

    # Redirect back to referring page or farmer profile
    return redirect(request.referrer or url_for('index'))

@app.route('/projects')
def projects():
    """Project listing route."""
    form = SearchForm(request.args)
    query = form.query.data
    category = form.category.data
    min_funding = form.min_funding.data
    max_funding = form.max_funding.data
    location = form.location.data

    # Base query
    project_query = Project.query

    # Apply filters
    if query:
        project_query = project_query.filter(
            (Project.title.ilike(f'%{query}%')) | 
            (Project.description.ilike(f'%{query}%'))
        )

    if category:
        project_query = project_query.filter(Project.category == category)

    if min_funding:
        project_query = project_query.filter(Project.funding_goal >= min_funding)

    if max_funding:
        project_query = project_query.filter(Project.funding_goal <= max_funding)

    if location:
        project_query = project_query.filter(Project.location.ilike(f'%{location}%'))

    # Get results and order by newest first
    projects = project_query.order_by(Project.created_at.desc()).all()

    return render_template('projects.html', 
                          title='Projects', 
                          app_name=APP_NAME,
                          projects=projects,
                          form=form)

@app.route('/project/new', methods=['GET', 'POST'])
@login_required
def new_project():
    """Create new project route."""
    if current_user.user_type != 'farmer':
        flash('Only farmers can create projects.', 'danger')
        return redirect(url_for('dashboard'))

    form = ProjectForm()
    if form.validate_on_submit():
        # Calculate end date based on duration
        end_date = datetime.datetime.utcnow() + datetime.timedelta(days=form.duration.data)

        project = Project(
            farmer_id=current_user.id,
            title=form.title.data,
            description=form.description.data,
            funding_goal=form.funding_goal.data,
            duration=form.duration.data,
            location=form.location.data,
            category=form.category.data,
            end_date=end_date
        )

        db.session.add(project)
        db.session.commit()

        flash('Your project has been created!', 'success')
        return redirect(url_for('project_detail', project_id=project.id))

    return render_template('project_detail.html', 
                          title='New Project', 
                          app_name=APP_NAME,
                          form=form, 
                          is_new=True)

@app.route('/project/<int:project_id>', methods=['GET', 'POST'])
def project_detail(project_id):
    """Project detail route."""
    project = Project.query.get_or_404(project_id)
    farmer = project.farmer

    # Editing project
    form = None
    if current_user.is_authenticated and current_user.id == project.farmer_id:
        form = ProjectForm()
        if form.validate_on_submit():
            project.title = form.title.data
            project.description = form.description.data
            project.funding_goal = form.funding_goal.data
            project.duration = form.duration.data
            project.location = form.location.data
            project.category = form.category.data

            # Update end date based on new duration
            project.end_date = datetime.datetime.utcnow() + datetime.timedelta(days=form.duration.data)

            db.session.commit()
            flash('Your project has been updated!', 'success')
            return redirect(url_for('project_detail', project_id=project_id))
        elif request.method == 'GET':
            form.title.data = project.title
            form.description.data = project.description
            form.funding_goal.data = project.funding_goal
            form.duration.data = project.duration
            form.location.data = project.location
            form.category.data = project.category

    # Investment form
    investment_form = None
    if current_user.is_authenticated and current_user.user_type == 'investor':
        investment_form = InvestmentForm()
        if investment_form.validate_on_submit():
            investment = Investment(
                investor_id=current_user.id,
                project_id=project_id,
                amount=investment_form.amount.data
            )

            db.session.add(investment)
            db.session.commit()

            flash('Your investment has been submitted!', 'success')
            return redirect(url_for('project_detail', project_id=project_id))

    # Get project investments and farmer information
    investments = project.investments.all()
    total_invested = project.total_invested
    progress = project.funding_percentage

    # Get farmer credibility score
    credibility_score = RecommendationEngine.get_farmer_credibility_score(farmer.id)

    # Get connection status if user is an investor
    connection_status = None
    if current_user.is_authenticated and current_user.user_type == 'investor':
        connection_status = current_user.get_connection_status(farmer)

    return render_template('project_detail.html', 
                          title=project.title, 
                          app_name=APP_NAME,
                          project=project, 
                          farmer=farmer,
                          form=form, 
                          investment_form=investment_form,
                          investments=investments,
                          total_invested=total_invested,
                          progress=progress,
                          is_new=False,
                          credibility_score=credibility_score,
                          connection_status=connection_status)

@app.route('/opportunities')
@login_required
def opportunities():
    """Investment opportunities route for investors."""
    if current_user.user_type != 'investor':
        flash('Only investors can view opportunities.', 'danger')
        return redirect(url_for('dashboard'))

    # Get recommended projects using the recommendation engine
    recommended_projects = RecommendationEngine.recommend_projects_to_investor(current_user.id)

    return render_template('opportunities.html', 
                          title='Investment Opportunities', 
                          app_name=APP_NAME,
                          projects=recommended_projects)

@app.route('/admin')
@login_required
def admin():
    """Admin management route."""
    if current_user.user_type != 'admin':
        flash('You do not have admin privileges.', 'danger')
        return redirect(url_for('dashboard'))

    users = User.query.all()
    farmers = User.query.filter_by(user_type='farmer').all()
    investors = User.query.filter_by(user_type='investor').all()
    projects = Project.query.all()

    return render_template('admin.html', 
                          title='Admin Panel', 
                          app_name=APP_NAME,
                          users=users,
                          farmers=farmers,
                          investors=investors,
                          projects=projects)

@app.route('/request_connection/<int:user_id>', methods=['POST'])
@login_required
def request_connection(user_id):
    """Request connection with another user."""
    user = User.query.get_or_404(user_id)

    # Prevent connecting with self or between same user types
    if user.id == current_user.id:
        flash('You cannot connect with yourself.', 'danger')
        return redirect(request.referrer or url_for('dashboard'))

    if user.user_type == current_user.user_type:
        flash(f'You cannot connect with another {current_user.user_type}.', 'danger')
        return redirect(request.referrer or url_for('dashboard'))

    # Send connection request
    if current_user.request_connection(user):
        flash(f'Connection request sent to {user.username}!', 'success')
    else:
        flash(f'Connection request could not be sent. You may already have a connection with {user.username}.', 'warning')

    return redirect(request.referrer or url_for('dashboard'))

@app.route('/accept_connection/<int:user_id>', methods=['POST'])
@login_required
def accept_connection(user_id):
    """Accept connection request from another user."""
    user = User.query.get_or_404(user_id)

    if current_user.accept_connection(user):
        flash(f'You are now connected with {user.username}!', 'success')
    else:
        flash('Connection request could not be accepted.', 'danger')

    return redirect(request.referrer or url_for('dashboard'))

@app.route('/reject_connection/<int:user_id>', methods=['POST'])
@login_required
def reject_connection(user_id):
    """Reject connection request from another user."""
    user = User.query.get_or_404(user_id)

    if current_user.reject_connection(user):
        flash(f'Connection request from {user.username} has been rejected.', 'info')
    else:
        flash('Connection request could not be rejected.', 'danger')

    return redirect(request.referrer or url_for('dashboard'))

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    """Contact form route."""
    form = ContactForm()
    if form.validate_on_submit():
        # For now, we'll just show a success message
        # In a real app, you would send an email or store the message
        flash('Your message has been sent! We will get back to you soon.', 'success')
        return redirect(url_for('contact'))

    return render_template('contact.html', title='Contact Us', app_name=APP_NAME, form=form)

@app.route('/message/<int:recipient_id>', methods=['GET', 'POST'])
@login_required
def send_message(recipient_id):
    """Route for sending messages between users."""
    recipient = User.query.get_or_404(recipient_id)

    # Check if users are connected
    if not current_user.is_connected_with(recipient_id) and current_user.user_type != 'admin':
        flash('You need to be connected with this user to send a message.', 'danger')
        return redirect(url_for('dashboard'))

    form = MessageForm()
    if form.validate_on_submit():
        message = Message(
            sender_id=current_user.id,
            recipient_id=recipient_id,
            subject=form.subject.data,
            content=form.content.data
        )

        db.session.add(message)
        db.session.commit()

        flash('Your message has been sent!', 'success')
        return redirect(url_for('chat', user_id=recipient_id))

    return render_template('send_message.html', 
                          title=f'Message to {recipient.username}', 
                          app_name=APP_NAME,
                          form=form, 
                          recipient=recipient)

@app.route('/chat/<int:user_id>')
@login_required
def chat(user_id):
    """Chat interface for communicating with connected users."""
    chat_partner = User.query.get_or_404(user_id)

    # Check if users are connected (admins can chat with anyone)
    if not current_user.is_connected_with(user_id) and current_user.user_type != 'admin':
        flash('You need to be connected with this user to chat.', 'danger')
        return redirect(url_for('dashboard'))

    # Get conversation messages
    sent_messages = Message.query.filter_by(
        sender_id=current_user.id, 
        recipient_id=user_id
    ).order_by(Message.created_at).all()

    received_messages = Message.query.filter_by(
        sender_id=user_id, 
        recipient_id=current_user.id
    ).order_by(Message.created_at).all()

    # Mark received messages as read
    for message in received_messages:
        if not message.read:
            message.read = True

    db.session.commit()

    # Combine and sort messages by timestamp
    messages = sorted(sent_messages + received_messages, key=lambda x: x.created_at)

    return render_template('chat.html', 
                          title=f'Chat with {chat_partner.username}', 
                          app_name=APP_NAME,
                          chat_partner=chat_partner, 
                          messages=messages)

# Import Flask-SocketIO functions
from flask_socketio import emit, join_room
# WebSocket setup for chat
@socketio.on('send_message')
def handle_message(data):
    """Handle chat messages through WebSocket."""
    sender_id = data.get('sender_id')
    recipient_id = data.get('recipient_id')
    content = data.get('content')
    subject = data.get('subject', 'Chat message')

    # Validate data
    if not all([sender_id, recipient_id, content]):
        return

    # Verify sender identity matches current user
    if int(sender_id) != current_user.id:
        return

    # Create and save the message
    message = Message(
        sender_id=int(sender_id),
        recipient_id=int(recipient_id),
        subject=subject,
        content=content
    )

    db.session.add(message)
    db.session.commit()

    # Emit message to recipient's room
    emit('new_message', {
        'id': message.id,
        'sender_id': message.sender_id,
        'recipient_id': message.recipient_id,
        'subject': message.subject,
        'content': message.content,
        'created_at': message.created_at.isoformat(),
        'sender_username': current_user.username
    }, to=f'user_{recipient_id}')

@socketio.on('connect')
def handle_connect():
    """Handle WebSocket connection."""
    if current_user.is_authenticated:
        # Join a room named after the user's ID
        room = f'user_{current_user.id}'
        join_room(room)
        logger.debug(f"User {current_user.username} joined room {room}")

@app.errorhandler(404)
def page_not_found(e):
    """404 error handler."""
    return render_template('error.html', title='Page Not Found', app_name=APP_NAME, error_code=404), 404

@app.errorhandler(500)
def internal_server_error(e):
    """500 error handler."""
    return render_template('error.html', title='Server Error', app_name=APP_NAME, error_code=500), 500

@app.context_processor
def utility_processor():
    """Add utility functions to template context."""
    return {
        'format_currency': format_currency,
        'format_date': format_date,
        'app_name': APP_NAME
    }