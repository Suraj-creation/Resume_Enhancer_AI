import io
import re
import os
from pdfminer.high_level import extract_text
from utils.pdf_processor import extract_text_from_pdf as pdf_processor_extract

# Re-export the extract_text_from_pdf function from pdf_processor
def extract_text_from_pdf(pdf_file, use_ocr=False):
    """
    Extract text from a PDF file using the pdf_processor module
    
    Args:
        pdf_file: Uploaded file object from Streamlit
        use_ocr: Boolean to force OCR processing
        
    Returns:
        str: Extracted text from the PDF
    """
    return pdf_processor_extract(pdf_file, use_ocr)

def calculate_industry_relevance(resume_text, industry):
    """
    Calculate the relevance of a resume to a specific industry
    
    Args:
        resume_text: String containing the resume text
        industry: String specifying the industry
        
    Returns:
        dict: Industry relevance scores and analysis
    """
    # Define industry-specific keywords for a few common industries
    industry_keywords = {
        "Technology": [
            "software", "developer", "programming", "java", "python", "javascript", 
            "cloud", "aws", "azure", "ai", "machine learning", "data science",
            "devops", "agile", "scrum", "frontend", "backend", "fullstack"
        ],
        "Finance": [
            "financial", "accounting", "investment", "banking", "portfolio",
            "analysis", "budget", "forecast", "profit", "loss", "revenue",
            "compliance", "risk", "audit", "tax", "regulatory", "fintech"
        ],
        "Healthcare": [
            "medical", "patient", "clinical", "health", "healthcare", "nurse",
            "doctor", "pharmaceutical", "therapy", "treatment", "diagnosis",
            "care", "hospital", "clinic", "EMR", "EHR", "HIPAA"
        ],
        "Marketing": [
            "marketing", "brand", "campaign", "social media", "content", "SEO",
            "analytics", "digital", "advertising", "market research", "audience",
            "engagement", "conversion", "strategy", "creative", "communications"
        ],
        "Education": [
            "teaching", "education", "curriculum", "instruction", "learning",
            "student", "classroom", "school", "university", "college", "professor",
            "academic", "course", "training", "development", "pedagogy"
        ],
        "Manufacturing": [
            "manufacturing", "production", "quality control", "assembly", "operations",
            "supply chain", "inventory", "logistics", "lean", "six sigma", "process improvement",
            "engineering", "maintenance", "safety", "compliance", "ISO"
        ]
    }
    
    # Default to Technology if industry not in our list
    keywords = industry_keywords.get(industry, industry_keywords["Technology"])
    
    # Count keyword occurrences
    keyword_count = 0
    keyword_matches = {}
    
    for keyword in keywords:
        count = len(re.findall(r'\b' + re.escape(keyword) + r'\b', resume_text.lower()))
        if count > 0:
            keyword_count += count
            keyword_matches[keyword] = count
    
    # Calculate a simple relevance score (0-100)
    max_expected_matches = 15  # Assuming a well-matched resume might have 15 keyword matches
    relevance_score = min(100, int((keyword_count / max_expected_matches) * 100))
    
    # Prepare the result
    result = {
        "score": relevance_score,
        "industry": industry,
        "keyword_matches": keyword_matches,
        "total_matches": keyword_count,
        "analysis": generate_industry_analysis(relevance_score, industry, keyword_matches)
    }
    
    return result

def generate_industry_analysis(score, industry, keyword_matches):
    """Generate a textual analysis of industry relevance"""
    if score >= 80:
        return f"Your resume shows strong alignment with the {industry} industry. It includes many relevant keywords and terms that employers in this field look for."
    elif score >= 60:
        return f"Your resume shows good alignment with the {industry} industry, but could benefit from more industry-specific terminology and experiences."
    elif score >= 40:
        return f"Your resume shows moderate alignment with the {industry} industry. Consider adding more relevant keywords and emphasizing industry-specific experiences."
    else:
        return f"Your resume could benefit from significant improvements to better align with the {industry} industry. Try incorporating more industry-specific terminology and highlighting relevant experiences."

def extract_and_rank_keywords(resume_text, job_description=None):
    """
    Extract keywords from resume and rank them by importance
    If job_description is provided, also rank based on relevance to the job
    
    Args:
        resume_text: String containing the resume text
        job_description: Optional string containing the job description
        
    Returns:
        dict: Ranked keywords and matching scores
    """
    # Common skill keywords across various industries
    skill_keywords = [
        # Technical skills
        "python", "java", "javascript", "c++", "c#", "ruby", "php", "html", "css",
        "aws", "azure", "gcp", "cloud", "docker", "kubernetes", "devops", "ci/cd",
        "machine learning", "ai", "artificial intelligence", "data science", "analytics",
        "sql", "nosql", "database", "big data", "tableau", "power bi", "excel",
        
        # Soft skills
        "leadership", "communication", "teamwork", "collaboration", "problem solving",
        "critical thinking", "time management", "project management", "agile", "scrum",
        "customer service", "negotiation", "presentation", "creativity", "innovation",
        
        # Business skills
        "strategy", "analysis", "research", "marketing", "sales", "business development",
        "operations", "finance", "accounting", "budget", "forecasting", "planning",
        "compliance", "legal", "regulatory", "risk management", "quality assurance"
    ]
    
    # Extract skills from the resume
    resume_skills = {}
    for skill in skill_keywords:
        count = len(re.findall(r'\b' + re.escape(skill) + r'\b', resume_text.lower()))
        if count > 0:
            resume_skills[skill] = count
    
    # If job description is provided, match against it
    job_match_score = {}
    overall_match_score = 0
    
    if job_description and job_description.strip():
        job_skills = {}
        for skill in skill_keywords:
            count = len(re.findall(r'\b' + re.escape(skill) + r'\b', job_description.lower()))
            if count > 0:
                job_skills[skill] = count
        
        # Calculate match scores for each skill
        for skill in resume_skills:
            if skill in job_skills:
                job_match_score[skill] = min(100, int((resume_skills[skill] / max(1, job_skills[skill])) * 100))
            else:
                job_match_score[skill] = 0
        
        # Calculate overall match percentage
        if job_skills:
            matched_skills = set(resume_skills.keys()).intersection(set(job_skills.keys()))
            overall_match_score = int((len(matched_skills) / len(job_skills)) * 100)
    
    # Rank skills by frequency in resume
    ranked_skills = {k: v for k, v in sorted(
        resume_skills.items(), key=lambda item: item[1], reverse=True
    )}
    
    return {
        "ranked_skills": ranked_skills,
        "job_match_score": job_match_score,
        "overall_match_percentage": overall_match_score,
        "missing_skills": get_missing_skills(resume_skills, job_description) if job_description else []
    }

def get_missing_skills(resume_skills, job_description):
    """
    Identify skills mentioned in the job description but missing from the resume
    
    Args:
        resume_skills: Dict of skills found in resume
        job_description: String containing the job description
        
    Returns:
        list: Skills mentioned in job description but not in resume
    """
    # Common skill keywords that might be in job descriptions
    common_job_skills = [
        # Technical skills
        "python", "java", "javascript", "c++", "c#", "ruby", "php", "html", "css",
        "aws", "azure", "gcp", "cloud", "docker", "kubernetes", "devops", "ci/cd",
        "machine learning", "ai", "artificial intelligence", "data science", "analytics",
        "sql", "nosql", "database", "big data", "tableau", "power bi", "excel",
        
        # Soft skills
        "leadership", "communication", "teamwork", "collaboration", "problem solving",
        "critical thinking", "time management", "project management", "agile", "scrum",
        "customer service", "negotiation", "presentation", "creativity", "innovation",
        
        # Business skills
        "strategy", "analysis", "research", "marketing", "sales", "business development",
        "operations", "finance", "accounting", "budget", "forecasting", "planning",
        "compliance", "legal", "regulatory", "risk management", "quality assurance"
    ]
    
    missing_skills = []
    
    for skill in common_job_skills:
        if skill not in resume_skills and re.search(r'\b' + re.escape(skill) + r'\b', job_description.lower()):
            missing_skills.append(skill)
    
    return missing_skills 