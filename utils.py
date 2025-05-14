import re
from models import User, Project, FarmerProfile, InvestorProfile

def is_valid_email(email):
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def get_user_projects(user_id):
    """Get projects created by a user."""
    return Project.get_by_farmer(user_id)

def get_matching_projects(investor_profile):
    """Get projects that match an investor's preferences."""
    matching_projects = []
    all_projects = Project.get_all_projects()
    
    if not investor_profile:
        return all_projects
    
    for project in all_projects:
        # Match by investment range
        if investor_profile.min_investment and project.funding_goal < investor_profile.min_investment:
            continue
        if investor_profile.max_investment and project.funding_goal > investor_profile.max_investment:
            continue
        
        # Match by location if specified
        if investor_profile.preferred_locations:
            locations = [loc.strip().lower() for loc in investor_profile.preferred_locations]
            if project.location.lower() not in locations and not any(loc in project.location.lower() for loc in locations):
                continue
        
        # Match by investment focus
        if investor_profile.investment_focus:
            if project.category not in investor_profile.investment_focus:
                continue
        
        matching_projects.append(project)
    
    return matching_projects

def get_matching_investors(project):
    """Get investors that might be interested in a project."""
    matching_investors = []
    
    for user in User.get_all_users():
        if user.user_type != 'investor' or not user.profile:
            continue
        
        investor_profile = user.profile
        
        # Match by investment range
        if investor_profile.min_investment and project.funding_goal < investor_profile.min_investment:
            continue
        if investor_profile.max_investment and project.funding_goal > investor_profile.max_investment:
            continue
        
        # Match by location if specified
        if investor_profile.preferred_locations:
            locations = [loc.strip().lower() for loc in investor_profile.preferred_locations]
            if project.location.lower() not in locations and not any(loc in project.location.lower() for loc in locations):
                continue
        
        # Match by investment focus
        if investor_profile.investment_focus:
            if project.category not in investor_profile.investment_focus:
                continue
        
        matching_investors.append(user)
    
    return matching_investors

def format_currency(amount):
    """Format a number as currency."""
    return f"${amount:,.2f}"

def format_date(timestamp):
    """Format a timestamp as a readable date."""
    from datetime import datetime
    dt = datetime.fromtimestamp(timestamp)
    return dt.strftime("%B %d, %Y")

def parse_comma_separated(text):
    """Parse a comma-separated string into a list."""
    if not text:
        return []
    return [item.strip() for item in text.split(',') if item.strip()]
