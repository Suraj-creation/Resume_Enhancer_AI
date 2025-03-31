"""
Job Matching Utilities - Functions for comparing resumes to job descriptions
"""

import re
import logging
import math
from collections import Counter
from typing import Dict, List, Set, Tuple, Any, Optional

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_job_keywords(job_description: str, max_keywords: int = 30) -> Dict[str, int]:
    """
    Extract important keywords from a job description.
    
    Args:
        job_description: The job description text
        max_keywords: Maximum number of keywords to extract
        
    Returns:
        Dictionary of keywords and their frequency
    """
    try:
        # Clean and normalize text
        text = job_description.lower()
        text = re.sub(r'[^\w\s]', ' ', text)  # Replace punctuation with spaces
        
        # Split into words
        words = text.split()
        
        # Remove common words and short words
        common_words = {
            'the', 'and', 'or', 'to', 'a', 'in', 'with', 'for', 'of', 'on', 'at', 'by', 
            'is', 'are', 'be', 'will', 'an', 'as', 'this', 'that', 'from', 'you', 'your',
            'we', 'our', 'their', 'they', 'it', 'have', 'has', 'had', 'not', 'but', 'if',
            'about', 'who', 'what', 'when', 'where', 'why', 'how', 'all', 'can', 'should',
            'would', 'other', 'which', 'such', 'them', 'these', 'some', 'than', 'its'
        }
        
        filtered_words = [word for word in words if word not in common_words and len(word) > 2]
        
        # Count word frequency
        word_counts = Counter(filtered_words)
        
        # Extract key phrases (basic implementation)
        phrases = []
        for i in range(len(words) - 1):
            if (words[i] not in common_words and len(words[i]) > 2 and 
                words[i+1] not in common_words and len(words[i+1]) > 2):
                phrases.append(f"{words[i]} {words[i+1]}")
        
        # Count phrase frequency
        phrase_counts = Counter(phrases)
        
        # Combine single words and phrases, prioritizing phrases
        combined_counts = {}
        
        # Add top phrases first
        for phrase, count in phrase_counts.most_common(max_keywords // 2):
            combined_counts[phrase] = count * 2  # Give phrases higher weight
        
        # Add top words next
        for word, count in word_counts.most_common(max_keywords):
            if len(combined_counts) >= max_keywords:
                break
            if not any(word in phrase for phrase in combined_counts.keys()):
                combined_counts[word] = count
        
        # Return top keywords
        return dict(Counter(combined_counts).most_common(max_keywords))
        
    except Exception as e:
        logger.error(f"Error extracting job keywords: {str(e)}")
        return {}

def extract_resume_keywords(resume_text: str, max_keywords: int = 50) -> Dict[str, int]:
    """
    Extract important keywords from a resume.
    
    Args:
        resume_text: The resume text
        max_keywords: Maximum number of keywords to extract
        
    Returns:
        Dictionary of keywords and their frequency
    """
    try:
        # Clean and normalize text
        text = resume_text.lower()
        text = re.sub(r'[^\w\s]', ' ', text)  # Replace punctuation with spaces
        
        # Split into words
        words = text.split()
        
        # Remove common words and short words
        common_words = {
            'the', 'and', 'or', 'to', 'a', 'in', 'with', 'for', 'of', 'on', 'at', 'by', 
            'is', 'are', 'be', 'will', 'an', 'as', 'this', 'that', 'from', 'you', 'your',
            'we', 'our', 'their', 'they', 'it', 'have', 'has', 'had', 'not', 'but', 'if',
            'about', 'who', 'what', 'when', 'where', 'why', 'how', 'all', 'can', 'should',
            'would', 'other', 'which', 'such', 'them', 'these', 'some', 'than', 'its'
        }
        
        filtered_words = [word for word in words if word not in common_words and len(word) > 2]
        
        # Count word frequency
        word_counts = Counter(filtered_words)
        
        # Extract key phrases (basic implementation)
        phrases = []
        for i in range(len(words) - 1):
            if (words[i] not in common_words and len(words[i]) > 2 and 
                words[i+1] not in common_words and len(words[i+1]) > 2):
                phrases.append(f"{words[i]} {words[i+1]}")
        
        # Count phrase frequency
        phrase_counts = Counter(phrases)
        
        # Combine single words and phrases
        combined_counts = {}
        
        # Add top phrases first
        for phrase, count in phrase_counts.most_common(max_keywords // 2):
            combined_counts[phrase] = count * 2  # Give phrases higher weight
        
        # Add top words next
        for word, count in word_counts.most_common(max_keywords):
            if len(combined_counts) >= max_keywords:
                break
            if not any(word in phrase for phrase in combined_counts.keys()):
                combined_counts[word] = count
        
        # Return top keywords
        return dict(Counter(combined_counts).most_common(max_keywords))
        
    except Exception as e:
        logger.error(f"Error extracting resume keywords: {str(e)}")
        return {}

def compare_resume_to_job(resume_text: str, job_description: str) -> Dict[str, Any]:
    """
    Compare a resume against a job description and return matching analysis.
    
    Args:
        resume_text: The resume text
        job_description: The job description text
        
    Returns:
        Dictionary with matching analysis results
    """
    try:
        # Extract keywords from both
        job_keywords = extract_job_keywords(job_description)
        resume_keywords = extract_resume_keywords(resume_text)
        
        # Find matching keywords
        matching_keywords = []
        for keyword in job_keywords:
            if keyword in resume_keywords:
                matching_keywords.append(keyword)
        
        # Find missing keywords
        missing_keywords = []
        for keyword in job_keywords:
            if keyword not in resume_keywords:
                missing_keywords.append(keyword)
        
        # Calculate match percentage
        if job_keywords:
            match_percentage = (len(matching_keywords) / len(job_keywords)) * 100
        else:
            match_percentage = 0
        
        # Look for skill mentions
        skills_pattern = r'skill(?:s|set)?(?::|\.|\s)?\s*(.*?)(?:\.|;|$)'
        skills_match = re.search(skills_pattern, job_description.lower())
        required_skills = []
        
        if skills_match:
            skills_text = skills_match.group(1)
            # Extract skills from the skills section
            skills_list = re.split(r',|\sand\s', skills_text)
            required_skills = [skill.strip() for skill in skills_list if skill.strip()]
        
        # Look for experience mentions
        experience_pattern = r'(\d+)(?:\+|\s*-\s*\d+)?\s*(?:year|yr)s?(?:\s+of)?\s+experience'
        experience_matches = re.findall(experience_pattern, job_description.lower())
        required_years = 0
        
        if experience_matches:
            # Convert to integers and take the maximum mentioned years
            years = [int(year) for year in experience_matches]
            required_years = max(years) if years else 0
        
        # Return results
        return {
            'job_keywords': job_keywords,
            'resume_keywords': resume_keywords,
            'matching_keywords': matching_keywords,
            'missing_keywords': missing_keywords,
            'match_percentage': match_percentage,
            'required_skills': required_skills,
            'required_years': required_years
        }
        
    except Exception as e:
        logger.error(f"Error comparing resume to job: {str(e)}")
        return {
            'job_keywords': {},
            'resume_keywords': {},
            'matching_keywords': [],
            'missing_keywords': [],
            'match_percentage': 0,
            'required_skills': [],
            'required_years': 0
        }

def calculate_match_percentage(resume_text: str, job_description: str) -> float:
    """
    Calculate the percentage match between a resume and job description.
    
    Args:
        resume_text: The resume text
        job_description: The job description text
        
    Returns:
        Match percentage (0-100)
    """
    try:
        # Get comparison results
        results = compare_resume_to_job(resume_text, job_description)
        
        # Return the match percentage
        return results.get('match_percentage', 0)
        
    except Exception as e:
        logger.error(f"Error calculating match percentage: {str(e)}")
        return 0

def get_missing_skills(resume_text: str, job_description: str) -> List[str]:
    """
    Get a list of skills mentioned in the job description but missing from the resume.
    
    Args:
        resume_text: The resume text
        job_description: The job description text
        
    Returns:
        List of missing skills
    """
    try:
        # Get comparison results
        results = compare_resume_to_job(resume_text, job_description)
        
        # Return the missing keywords
        return results.get('missing_keywords', [])
        
    except Exception as e:
        logger.error(f"Error getting missing skills: {str(e)}")
        return []

def generate_improvement_suggestions(resume_text: str, job_description: str) -> List[str]:
    """
    Generate suggestions for improving the resume to better match the job description.
    
    Args:
        resume_text: The resume text
        job_description: The job description text
        
    Returns:
        List of improvement suggestions
    """
    try:
        # Get comparison results
        results = compare_resume_to_job(resume_text, job_description)
        
        suggestions = []
        
        # Add missing keywords suggestion
        missing_keywords = results.get('missing_keywords', [])
        if missing_keywords:
            top_missing = missing_keywords[:5]  # Get top 5 missing keywords
            suggestions.append(f"Add these keywords to your resume: {', '.join(top_missing)}")
        
        # Check for required years of experience
        required_years = results.get('required_years', 0)
        if required_years > 0:
            exp_pattern = r'(\d+)(?:\+|\s*-\s*\d+)?\s*(?:year|yr)s?(?:\s+of)?\s+experience'
            resume_exp_matches = re.findall(exp_pattern, resume_text.lower())
            resume_years = [int(year) for year in resume_exp_matches]
            max_resume_years = max(resume_years) if resume_years else 0
            
            if max_resume_years < required_years:
                suggestions.append(f"Highlight your {required_years}+ years of experience if you have it")
        
        # Check for quantifiable achievements
        if not re.search(r'\d+%|\d+\s*x|\$\s*\d+', resume_text):
            suggestions.append("Add quantifiable achievements (e.g., 'increased sales by 20%')")
        
        # Check if resume length seems appropriate
        words_in_resume = len(resume_text.split())
        if words_in_resume < 200:
            suggestions.append("Your resume seems short. Consider adding more details about your experience")
        elif words_in_resume > 1000:
            suggestions.append("Your resume is quite long. Consider focusing on the most relevant experience")
        
        # Check for soft skills
        soft_skills = ['communication', 'leadership', 'teamwork', 'problem solving', 
                      'time management', 'adaptability', 'creativity', 'critical thinking']
        if any(skill in job_description.lower() for skill in soft_skills):
            if not any(skill in resume_text.lower() for skill in soft_skills):
                suggestions.append("Include relevant soft skills mentioned in the job description")
        
        # Additional suggestions
        suggestions.append("Tailor your resume summary/objective to match this specific job")
        suggestions.append("Reorder your experience to highlight the most relevant items first")
        
        return suggestions
        
    except Exception as e:
        logger.error(f"Error generating improvement suggestions: {str(e)}")
        return ["Add missing keywords from the job description", 
                "Tailor your resume for this specific position"]

def get_matching_score_details(resume_text: str, job_description: str) -> Dict[str, Any]:
    """
    Get detailed scores for different aspects of the resume match.
    
    Args:
        resume_text: The resume text
        job_description: The job description text
        
    Returns:
        Dictionary with detailed scores
    """
    try:
        # Get comparison results
        results = compare_resume_to_job(resume_text, job_description)
        
        # Calculate detailed scores
        keyword_match = results.get('match_percentage', 0)
        
        # Skills match (percentage of required skills found in resume)
        required_skills = results.get('required_skills', [])
        skills_found = 0
        
        for skill in required_skills:
            if skill.lower() in resume_text.lower():
                skills_found += 1
        
        skills_match = (skills_found / len(required_skills) * 100) if required_skills else 0
        
        # Experience match
        required_years = results.get('required_years', 0)
        exp_pattern = r'(\d+)(?:\+|\s*-\s*\d+)?\s*(?:year|yr)s?(?:\s+of)?\s+experience'
        resume_exp_matches = re.findall(exp_pattern, resume_text.lower())
        resume_years = [int(year) for year in resume_exp_matches]
        max_resume_years = max(resume_years) if resume_years else 0
        
        if required_years == 0:
            experience_match = 100  # No specific requirement
        else:
            experience_match = min(max_resume_years / required_years * 100, 100)
        
        # Overall match (weighted average)
        overall_match = (keyword_match * 0.6 + skills_match * 0.3 + experience_match * 0.1)
        
        return {
            'overall_match': overall_match,
            'keyword_match': keyword_match,
            'skills_match': skills_match,
            'experience_match': experience_match
        }
        
    except Exception as e:
        logger.error(f"Error calculating detailed match scores: {str(e)}")
        return {
            'overall_match': 0,
            'keyword_match': 0,
            'skills_match': 0,
            'experience_match': 0
        } 