import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from models import User, FarmerProfile, InvestorProfile, Project, FarmerRating
import logging

logger = logging.getLogger(__name__)

class RecommendationEngine:
    """
    Recommendation engine for AgriBridge that combines content-based 
    and collaborative filtering to connect farmers and investors.
    """
    
    @staticmethod
    def get_similar_farms(farmer_id, n=5):
        """
        Get similar farms to the given farmer using content-based filtering.
        
        Args:
            farmer_id: ID of the farmer to find similar farms for
            n: Number of similar farms to return
            
        Returns:
            List of similar FarmerProfile objects
        """
        try:
            # Get the farmer's profile
            farmer = User.query.get(farmer_id)
            if not farmer or farmer.user_type != 'farmer' or not farmer.farmer_profile:
                return []
                
            # Get all farmer profiles
            all_farmers = User.query.filter_by(user_type='farmer').all()
            farmer_profiles = [f.farmer_profile for f in all_farmers if f.farmer_profile]
            
            if len(farmer_profiles) < 2:  # Need at least 2 farmers for comparison
                return []
                
            # Create feature vectors for content-based filtering
            features = []
            farmer_ids = []
            
            for profile in farmer_profiles:
                # Combine various farm features into a single text representation
                crops = profile.crops or ''
                technologies = profile.technologies or ''
                description = profile.description or ''
                location = profile.location or ''
                
                # Create a combined feature text
                feature_text = f"{crops} {technologies} {description} {location}"
                features.append(feature_text)
                farmer_ids.append(profile.user_id)
            
            # Transform features into TF-IDF vectors
            tfidf = TfidfVectorizer(stop_words='english')
            tfidf_matrix = tfidf.fit_transform(features)
            
            # Calculate cosine similarity between farms
            cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)
            
            # Get the index of the target farmer
            idx = farmer_ids.index(farmer_id)
            
            # Get similarity scores with other farmers
            sim_scores = list(enumerate(cosine_sim[idx]))
            
            # Filter out the farmer itself
            sim_scores = [s for s in sim_scores if s[0] != idx]
            
            # Sort farmers by similarity score
            sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
            
            # Get top N similar farms
            sim_scores = sim_scores[:n]
            similar_farm_indices = [i[0] for i in sim_scores]
            
            # Get the farmer profiles for these indices
            similar_farms = [farmer_profiles[i] for i in similar_farm_indices]
            
            return similar_farms
        except Exception as e:
            logger.error(f"Error getting similar farms: {str(e)}")
            return []
    
    @staticmethod
    def get_farmer_credibility_score(farmer_id):
        """
        Calculate a credibility score for a farmer based on ratings,
        project success, and other factors.
        
        Args:
            farmer_id: ID of the farmer
            
        Returns:
            Credibility score between 0 and 100
        """
        try:
            farmer = User.query.get(farmer_id)
            if not farmer or farmer.user_type != 'farmer':
                return 0
                
            # Get average rating (0-5 scale)
            avg_rating = farmer.get_avg_rating() or 0
            
            # Convert rating to 0-50 scale (50% of total score)
            rating_score = (avg_rating / 5) * 50
            
            # Calculate project success rate (percentage of projects that reached funding goals)
            projects = farmer.projects.all()
            if not projects:
                project_success_score = 0
            else:
                successful_projects = sum(1 for p in projects if p.funding_percentage >= 100)
                project_success_rate = successful_projects / len(projects)
                project_success_score = project_success_rate * 25  # 25% of total score
            
            # Account for experience (based on number of projects and time on platform)
            num_projects = len(projects)
            experience_score = min(25, num_projects * 5)  # 25% of total score, max out at 5 projects
            
            # Calculate total credibility score
            total_score = rating_score + project_success_score + experience_score
            
            return round(total_score, 1)
        except Exception as e:
            logger.error(f"Error calculating farmer credibility: {str(e)}")
            return 0
    
    @staticmethod
    def recommend_projects_to_investor(investor_id, n=10):
        """
        Recommend projects to an investor using a hybrid of content-based and 
        collaborative filtering approaches.
        
        Args:
            investor_id: ID of the investor to recommend projects to
            n: Number of projects to recommend
            
        Returns:
            List of recommended Project objects
        """
        try:
            investor = User.query.get(investor_id)
            if not investor or investor.user_type != 'investor' or not investor.investor_profile:
                return []
                
            # Get all projects
            all_projects = Project.query.all()
            if not all_projects:
                return []
            
            # Get investor's preferences
            investor_profile = investor.investor_profile
            focus_areas = investor_profile.get_investment_focus_list()
            preferred_locations = investor_profile.get_preferred_locations_list()
            min_investment = investor_profile.min_investment
            max_investment = investor_profile.max_investment
            
            # Initial filtering based on investment amount
            if max_investment > 0:
                filtered_projects = [p for p in all_projects if p.funding_goal <= max_investment]
            else:
                filtered_projects = all_projects
                
            if min_investment > 0:
                filtered_projects = [p for p in filtered_projects if p.funding_goal >= min_investment]
            
            # Content-based filtering
            project_scores = []
            
            for project in filtered_projects:
                score = 0
                
                # Location match
                if preferred_locations and any(loc.lower() in project.location.lower() for loc in preferred_locations):
                    score += 3
                    
                # Category match with investment focus
                if focus_areas and project.category in focus_areas:
                    score += 4
                
                # Farmer credibility score (0-100) - scale to 0-3 points
                farmer = project.farmer
                credibility_score = RecommendationEngine.get_farmer_credibility_score(farmer.id)
                score += (credibility_score / 100) * 3
                
                project_scores.append((project, score))
            
            # Sort projects by score (descending)
            sorted_projects = sorted(project_scores, key=lambda x: x[1], reverse=True)
            
            # Get top N projects
            top_projects = [p[0] for p in sorted_projects[:n]]
            
            return top_projects
        except Exception as e:
            logger.error(f"Error recommending projects to investor: {str(e)}")
            return []
    
    @staticmethod
    def recommend_investors_to_farmer(farmer_id, n=10):
        """
        Recommend investors to a farmer based on investment preferences and project matches.
        
        Args:
            farmer_id: ID of the farmer to recommend investors to
            n: Number of investors to recommend
            
        Returns:
            List of recommended User objects (investors)
        """
        try:
            farmer = User.query.get(farmer_id)
            if not farmer or farmer.user_type != 'farmer' or not farmer.farmer_profile:
                return []
                
            # Get all investors
            all_investors = User.query.filter_by(user_type='investor').all()
            if not all_investors:
                return []
            
            # Get farmer's projects
            projects = farmer.projects.all()
            if not projects:
                # If farmer has no projects, recommend based on farm profile
                return RecommendationEngine._recommend_investors_by_farm_profile(farmer, all_investors, n)
            
            # Calculate match scores for each investor
            investor_scores = []
            
            for investor in all_investors:
                if not investor.investor_profile:
                    continue
                    
                score = 0
                investor_profile = investor.investor_profile
                
                # Check location preferences
                preferred_locations = investor_profile.get_preferred_locations_list()
                farmer_location = farmer.farmer_profile.location
                
                if preferred_locations and any(loc.lower() in farmer_location.lower() for loc in preferred_locations):
                    score += 2
                
                # Check investment focus against farmer's crops/technologies
                focus_areas = investor_profile.get_investment_focus_list()
                farmer_crops = farmer.farmer_profile.get_crops_list()
                farmer_techs = farmer.farmer_profile.get_technologies_list()
                
                if focus_areas:
                    # Compare focus areas with farmer's crops and technologies
                    if any(focus.lower() in ' '.join(farmer_crops).lower() for focus in focus_areas):
                        score += 2
                    if any(focus.lower() in ' '.join(farmer_techs).lower() for focus in focus_areas):
                        score += 2
                
                # Check if investor's budget matches farmer's projects
                min_investment = investor_profile.min_investment
                max_investment = investor_profile.max_investment
                
                if max_investment > 0:
                    matching_projects = [p for p in projects if p.funding_goal <= max_investment]
                    if matching_projects:
                        score += 3
                
                investor_scores.append((investor, score))
            
            # Sort investors by score (descending)
            sorted_investors = sorted(investor_scores, key=lambda x: x[1], reverse=True)
            
            # Get top N investors
            top_investors = [i[0] for i in sorted_investors[:n]]
            
            return top_investors
        except Exception as e:
            logger.error(f"Error recommending investors to farmer: {str(e)}")
            return []
    
    @staticmethod
    def _recommend_investors_by_farm_profile(farmer, all_investors, n=10):
        """
        Recommend investors to a farmer based solely on farm profile.
        Used when the farmer has no projects.
        
        Args:
            farmer: Farmer user object
            all_investors: List of all investor user objects
            n: Number of investors to recommend
            
        Returns:
            List of recommended User objects (investors)
        """
        investor_scores = []
        
        for investor in all_investors:
            if not investor.investor_profile:
                continue
                
            score = 0
            investor_profile = investor.investor_profile
            
            # Check location preferences
            preferred_locations = investor_profile.get_preferred_locations_list()
            farmer_location = farmer.farmer_profile.location
            
            if preferred_locations and any(loc.lower() in farmer_location.lower() for loc in preferred_locations):
                score += 3
            
            # Check investment focus against farmer's crops/technologies
            focus_areas = investor_profile.get_investment_focus_list()
            farmer_crops = farmer.farmer_profile.get_crops_list()
            farmer_techs = farmer.farmer_profile.get_technologies_list()
            
            if focus_areas:
                if any(focus.lower() in ' '.join(farmer_crops).lower() for focus in focus_areas):
                    score += 3
                if any(focus.lower() in ' '.join(farmer_techs).lower() for focus in focus_areas):
                    score += 3
            
            investor_scores.append((investor, score))
        
        # Sort investors by score (descending)
        sorted_investors = sorted(investor_scores, key=lambda x: x[1], reverse=True)
        
        # Get top N investors
        top_investors = [i[0] for i in sorted_investors[:n]]
        
        return top_investors