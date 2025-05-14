from flask import render_template, url_for, flash, redirect, request, session, abort
from flask_login import login_user, logout_user, current_user, login_required
from app import app
from models import User, FarmerProfile, InvestorProfile, Project, Investment, Message
from forms import (
    LoginForm, RegistrationForm, FarmerProfileForm, InvestorProfileForm, 
    ProjectForm, InvestmentForm, ContactForm, MessageForm, SearchForm
)
from utils import get_matching_projects, get_user_projects, parse_comma_separated, format_currency, format_date

@app.route('/')
def index():
    """Homepage route."""
    # Get featured projects
    featured_projects = Project.get_all_projects()[:6]
    return render_template('index.html', 
                          title='Home', 
                          projects=featured_projects)

@app.route('/about')
def about():
    """About page route."""
    return render_template('about.html', title='About Us')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login route."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.get_by_email(form.email.data)
        if user and user.check_password(form.password.data):
            login_user(user)
            flash('Login successful!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard'))
        else:
            flash('Login unsuccessful. Please check email and password.', 'danger')
    
    return render_template('login.html', title='Login', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration route."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user_id = User.get_next_id()
        user = User(
            id=user_id,
            username=form.username.data,
            email=form.email.data,
            user_type=form.user_type.data,
            password=form.password.data
        )
        user.save()
        flash(f'Account created successfully! You can now log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', title='Register', form=form)

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
        projects = get_user_projects(current_user.id)
        return render_template('dashboard.html', 
                              title='Farmer Dashboard', 
                              projects=projects)
    else:  # investor
        matching_projects = get_matching_projects(current_user.profile)
        investments = Investment.get_by_investor(current_user.id)
        return render_template('dashboard.html', 
                              title='Investor Dashboard', 
                              projects=matching_projects,
                              investments=investments)

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """User profile route."""
    if current_user.user_type == 'farmer':
        form = FarmerProfileForm()
        
        if form.validate_on_submit():
            profile = FarmerProfile(
                user_id=current_user.id,
                farm_name=form.farm_name.data,
                location=form.location.data,
                size=form.size.data,
                description=form.description.data,
                crops=parse_comma_separated(form.crops.data),
                technologies=parse_comma_separated(form.technologies.data)
            )
            profile.save()
            flash('Your farmer profile has been updated!', 'success')
            return redirect(url_for('dashboard'))
        
        # Pre-fill form if profile exists
        elif current_user.profile:
            form.farm_name.data = current_user.profile.farm_name
            form.location.data = current_user.profile.location
            form.size.data = current_user.profile.size
            form.description.data = current_user.profile.description
            form.crops.data = ', '.join(current_user.profile.crops)
            form.technologies.data = ', '.join(current_user.profile.technologies)
        
        return render_template('farmer_profile.html', title='Farmer Profile', form=form)
    
    else:  # investor
        form = InvestorProfileForm()
        
        if form.validate_on_submit():
            profile = InvestorProfile(
                user_id=current_user.id,
                company_name=form.company_name.data,
                investment_focus=form.investment_focus.data,
                min_investment=form.min_investment.data,
                max_investment=form.max_investment.data,
                preferred_locations=parse_comma_separated(form.preferred_locations.data),
                interests=form.interests.data
            )
            profile.save()
            flash('Your investor profile has been updated!', 'success')
            return redirect(url_for('dashboard'))
        
        # Pre-fill form if profile exists
        elif current_user.profile:
            form.company_name.data = current_user.profile.company_name
            form.investment_focus.data = current_user.profile.investment_focus
            form.min_investment.data = current_user.profile.min_investment
            form.max_investment.data = current_user.profile.max_investment
            form.preferred_locations.data = ', '.join(current_user.profile.preferred_locations)
            form.interests.data = current_user.profile.interests
        
        return render_template('investor_profile.html', title='Investor Profile', form=form)

@app.route('/projects')
def projects():
    """Project listing route."""
    form = SearchForm(request.args)
    query = form.query.data
    category = form.category.data
    min_funding = form.min_funding.data
    max_funding = form.max_funding.data
    location = form.location.data
    
    all_projects = Project.get_all_projects()
    
    # Filter projects based on search criteria
    filtered_projects = []
    for project in all_projects:
        # Filter by query
        if query and query.lower() not in project.title.lower() and query.lower() not in project.description.lower():
            continue
        
        # Filter by category
        if category and project.category != category:
            continue
        
        # Filter by funding
        if min_funding and project.funding_goal < min_funding:
            continue
        if max_funding and project.funding_goal > max_funding:
            continue
        
        # Filter by location
        if location and location.lower() not in project.location.lower():
            continue
        
        filtered_projects.append(project)
    
    return render_template('projects.html', 
                          title='Projects', 
                          projects=filtered_projects,
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
        project_id = Project.get_next_id()
        project = Project(
            id=project_id,
            farmer_id=current_user.id,
            title=form.title.data,
            description=form.description.data,
            funding_goal=form.funding_goal.data,
            duration=form.duration.data,
            location=form.location.data,
            category=form.category.data
        )
        project.save()
        flash('Your project has been created!', 'success')
        return redirect(url_for('project_detail', project_id=project_id))
    
    return render_template('project_detail.html', 
                          title='New Project', 
                          form=form, 
                          is_new=True)

@app.route('/project/<int:project_id>', methods=['GET', 'POST'])
def project_detail(project_id):
    """Project detail route."""
    project = Project.get_by_id(project_id)
    if not project:
        abort(404)
    
    farmer = User.get_by_id(project.farmer_id)
    
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
            project.save()
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
            investment_id = Investment.get_next_id()
            investment = Investment(
                id=investment_id,
                investor_id=current_user.id,
                project_id=project_id,
                amount=investment_form.amount.data
            )
            investment.save()
            flash('Your investment has been submitted!', 'success')
            return redirect(url_for('project_detail', project_id=project_id))
    
    # Get project investments
    investments = Investment.get_by_project(project_id)
    total_invested = sum(inv.amount for inv in investments)
    progress = (total_invested / project.funding_goal) * 100 if project.funding_goal > 0 else 0
    
    return render_template('project_detail.html', 
                          title=project.title, 
                          project=project, 
                          farmer=farmer,
                          form=form, 
                          investment_form=investment_form,
                          investments=investments,
                          total_invested=total_invested,
                          progress=progress,
                          is_new=False)

@app.route('/opportunities')
@login_required
def opportunities():
    """Investment opportunities route for investors."""
    if current_user.user_type != 'investor':
        flash('Only investors can view opportunities.', 'danger')
        return redirect(url_for('dashboard'))
    
    matching_projects = get_matching_projects(current_user.profile)
    return render_template('opportunities.html', 
                          title='Investment Opportunities', 
                          projects=matching_projects)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    """Contact form route."""
    form = ContactForm()
    if form.validate_on_submit():
        flash('Your message has been sent! We will get back to you soon.', 'success')
        return redirect(url_for('contact'))
    
    return render_template('contact.html', title='Contact Us', form=form)

@app.route('/message/<int:recipient_id>', methods=['GET', 'POST'])
@login_required
def send_message(recipient_id):
    """Route for sending messages between users."""
    recipient = User.get_by_id(recipient_id)
    if not recipient:
        abort(404)
    
    form = MessageForm()
    if form.validate_on_submit():
        message_id = Message.get_next_id()
        message = Message(
            id=message_id,
            sender_id=current_user.id,
            recipient_id=recipient_id,
            subject=form.subject.data,
            content=form.content.data
        )
        message.save()
        flash('Your message has been sent!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('contact.html', 
                          title=f'Message to {recipient.username}', 
                          form=form, 
                          recipient=recipient)

@app.errorhandler(404)
def page_not_found(e):
    """404 error handler."""
    return render_template('error.html', title='Page Not Found', error_code=404), 404

@app.errorhandler(500)
def internal_server_error(e):
    """500 error handler."""
    return render_template('error.html', title='Server Error', error_code=500), 500

@app.context_processor
def utility_processor():
    """Add utility functions to template context."""
    return {
        'format_currency': format_currency,
        'format_date': format_date
    }
