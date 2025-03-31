"""
Job Matcher Service - Provides AI-powered job matching and resume tailoring
"""

import logging
import streamlit as st
from typing import Dict, List, Any, Optional, Union
import re

from utils.ai_services.service_manager import AIServiceManager

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class JobMatcherService:
    """Service for matching resumes to job descriptions and tailoring resumes"""
    
    def __init__(self, api_key=None):
        """
        Initialize the Job Matcher service
        
        Args:
            api_key (str, optional): Not used directly, but kept for API compatibility
        """
        # Get the service manager
        self.service_manager = AIServiceManager()
        
        # Try to get Gemini service
        self.gemini = self.service_manager.get_service("gemini")
        
        # Try to get HuggingFace service
        self.huggingface = self.service_manager.get_service("huggingface")
        
        # Try to get Resume Analyzer service
        self.resume_analyzer = self.service_manager.get_service("resume_analyzer")
        
        # Set availability flags
        self.gemini_available = self.gemini is not None
        self.huggingface_available = self.huggingface is not None
        self.resume_analyzer_available = self.resume_analyzer is not None
        
    def analyze_job_description(self, job_description):
        """
        Analyze a job description to extract key information
        
        Args:
            job_description (str): Job description text
            
        Returns:
            dict: Extracted information from the job description
        """
        # If Gemini is available, use it for detailed analysis
        if self.gemini_available:
            try:
                return self.gemini.extract_keywords_from_job(job_description)
            except Exception as e:
                logger.error(f"Error analyzing job description with Gemini: {str(e)}")
                # Fall back to basic analysis
                
        # Basic job description analysis
        # Define common categories and keywords
        categories = {
            "required_technical_skills": [
                "python", "java", "javascript", "c++", "c#", "ruby", "php", "html", "css",
                "react", "angular", "vue", "node.js", "django", "flask", "spring", "express",
                "aws", "azure", "gcp", "cloud", "docker", "kubernetes", "devops", "ci/cd",
                "machine learning", "ai", "artificial intelligence", "data science", "analytics",
                "sql", "nosql", "database", "mongodb", "mysql", "postgresql", "oracle",
                "excel", "tableau", "power bi", "git", "github", "jira", "confluence"
            ],
            "required_soft_skills": [
                "leadership", "communication", "teamwork", "collaboration", "problem solving",
                "critical thinking", "time management", "project management", "agile", "scrum",
                "customer service", "interpersonal", "adaptability", "flexibility", "creativity"
            ],
            "education_requirements": [
                "bachelor", "master", "phd", "doctorate", "mba", "degree", "university",
                "college", "certification", "diploma", "graduate"
            ],
            "experience_requirements": [
                "years of experience", "year experience", "junior", "senior", "lead",
                "entry level", "mid level", "principal", "manager", "director"
            ]
        }
        
        # Extract keywords by category
        results = {}
        for category, keywords in categories.items():
            category_matches = []
            for keyword in keywords:
                # Look for matches, considering word boundaries
                if re.search(r'\b' + re.escape(keyword) + r'\b', job_description.lower()):
                    category_matches.append(keyword)
            results[category] = category_matches
            
        # Extract key responsibilities
        responsibilities = []
        responsibility_patterns = [
            r'Responsibilities[:\n]+(.+?)(?=\n\n|\n[A-Z])',
            r'Key Duties[:\n]+(.+?)(?=\n\n|\n[A-Z])',
            r'Job Duties[:\n]+(.+?)(?=\n\n|\n[A-Z])',
            r'What You\'ll Do[:\n]+(.+?)(?=\n\n|\n[A-Z])'
        ]
        
        for pattern in responsibility_patterns:
            matches = re.findall(pattern, job_description, re.DOTALL | re.IGNORECASE)
            if matches:
                # Process the matched text to extract bullet points
                resp_text = matches[0]
                # Look for bullet points
                bullets = re.findall(r'[•\-*]\s*(.+?)(?=\n[•\-*]|\n\n|$)', resp_text, re.DOTALL)
                if bullets:
                    responsibilities.extend(bullets)
                else:
                    # If no bullets, split by newlines
                    lines = [line.strip() for line in resp_text.split('\n') if line.strip()]
                    responsibilities.extend(lines)
                
        results["key_responsibilities"] = responsibilities
            
        return results
        
    def match_resume_to_job(self, resume_sections, job_description):
        """
        Match a resume against a job description
        
        Args:
            resume_sections (dict): Dictionary of resume sections
            job_description (str): Job description text
            
        Returns:
            dict: Matching results and recommendations
        """
        # If Resume Analyzer is available, use it for matching
        if self.resume_analyzer_available:
            try:
                return self.resume_analyzer.match_to_job(resume_sections, job_description)
            except Exception as e:
                logger.error(f"Error matching with Resume Analyzer: {str(e)}")
                # Fall back to direct Gemini and HuggingFace
        
        # If Gemini is available, use it for comprehensive matching
        if self.gemini_available:
            try:
                match_results = self.gemini.match_resume_to_job(resume_sections, job_description)
                
                # If HuggingFace is available, enhance with additional analysis
                if self.huggingface_available:
                    try:
                        hf_match = self.huggingface.match_resume_to_job(resume_sections, job_description)
                        
                        # Merge the results, preferring Gemini for overall structure
                        # but adding HuggingFace's detailed analysis
                        if "match_details" in hf_match:
                            match_results["match_details"] = hf_match["match_details"]
                            
                        # Add any additional missing keywords
                        if "missing_keywords" in hf_match:
                            match_results["missing_keywords"] = list(set(
                                match_results.get("missing_keywords", []) + 
                                hf_match.get("missing_keywords", [])
                            ))
                            
                    except Exception as e:
                        logger.error(f"Error enhancing match with HuggingFace: {str(e)}")
                        
                return match_results
                
            except Exception as e:
                logger.error(f"Error matching with Gemini: {str(e)}")
                # Fall back to HuggingFace
                
        # If Gemini failed or is not available, try HuggingFace
        if self.huggingface_available:
            try:
                return self.huggingface.match_resume_to_job(resume_sections, job_description)
            except Exception as e:
                logger.error(f"Error matching with HuggingFace: {str(e)}")
                # Fall back to basic matching
                
        # Basic matching as a last resort
        return self._basic_match(resume_sections, job_description)
        
    def _basic_match(self, resume_sections, job_description):
        """Basic resume-job matching when AI services are unavailable"""
        # Create a single string with all resume content
        resume_text = ""
        for section_name, content in resume_sections.items():
            if section_name not in ["full_text", "_match_results"] and content != "Missing":
                resume_text += f"{content}\n\n"
                
        # Extract words from resume and job description
        resume_words = set(re.findall(r'\b\w+\b', resume_text.lower()))
        job_words = set(re.findall(r'\b\w+\b', job_description.lower()))
        
        # Find matching and missing words
        matching_words = resume_words.intersection(job_words)
        missing_words = job_words - resume_words
        
        # Filter out common words
        common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
                        'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
                        'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'shall',
                        'should', 'can', 'could', 'may', 'might', 'must', 'of', 'from', 'as'}
        
        matching_keywords = [word for word in matching_words if word not in common_words and len(word) > 3]
        missing_keywords = [word for word in missing_words if word not in common_words and len(word) > 3]
        
        # Calculate match percentage
        if len(job_words - common_words) > 0:
            match_percentage = int((len(matching_keywords) / len(job_words - common_words)) * 100)
        else:
            match_percentage = 0
            
        # Limit to top keywords
        matching_keywords = matching_keywords[:20]
        missing_keywords = missing_keywords[:20]
        
        # Generate basic improvement suggestions
        improvement_suggestions = [
            "Add the missing keywords to your resume",
            "Highlight experiences relevant to the job description",
            "Quantify your achievements with metrics",
            "Use industry-specific terminology from the job description",
            "Tailor your summary to match the job requirements"
        ]
        
        return {
            "match_percentage": match_percentage,
            "matching_keywords": matching_keywords,
            "missing_keywords": missing_keywords,
            "section_scores": {
                "skills": match_percentage,
                "experience": match_percentage,
                "education": match_percentage,
                "overall": match_percentage
            },
            "improvement_suggestions": improvement_suggestions
        }
        
    def generate_tailored_resume(self, resume_sections, job_description):
        """
        Generate a fully tailored resume based on a job description
        
        Args:
            resume_sections (dict): Dictionary of resume sections
            job_description (str): Job description text
            
        Returns:
            dict: Dictionary of tailored resume sections
        """
        # If Resume Analyzer is available, use it for tailoring
        if self.resume_analyzer_available:
            try:
                return self.resume_analyzer.generate_tailored_resume(resume_sections, job_description)
            except Exception as e:
                logger.error(f"Error tailoring with Resume Analyzer: {str(e)}")
                # Fall back to direct Gemini
                
        # If Gemini is available, use it for comprehensive tailoring
        if self.gemini_available:
            try:
                return self.gemini.generate_tailored_resume(resume_sections, job_description)
            except Exception as e:
                logger.error(f"Error tailoring with Gemini: {str(e)}")
                # Fall back to section-by-section enhancement
                
        # Enhance each section individually
        # First, get match results for reference
        match_results = self.match_resume_to_job(resume_sections, job_description)
        
        # Then enhance each section
        tailored_sections = {}
        
        for section_name, content in resume_sections.items():
            # Skip full_text or missing sections
            if section_name == "full_text" or content == "Missing":
                tailored_sections[section_name] = content
                continue
                
            # Enhance the section
            tailored_sections[section_name] = self._enhance_section(
                section_name, content, job_description, match_results
            )
            
        # Add match results for reference
        tailored_sections["_match_results"] = match_results
        
        return tailored_sections
        
    def _enhance_section(self, section_name, section_content, job_description, match_results):
        """
        Enhance a resume section for a specific job
        
        Args:
            section_name (str): Section name
            section_content (str): Section content
            job_description (str): Job description text
            match_results (dict): Results of resume-job matching
            
        Returns:
            str: Enhanced section content
        """
        # If Gemini is available, use it
        if self.gemini_available:
            try:
                return self.gemini.enhance_resume_section(section_name, section_content, job_description)
            except Exception as e:
                logger.error(f"Error enhancing {section_name} with Gemini: {str(e)}")
                
        # If HuggingFace is available, use it
        if self.huggingface_available:
            try:
                # Get missing keywords from match results
                missing_keywords = match_results.get("missing_keywords", [])[:5]
                
                # If we have missing keywords, use them to enhance the section
                if missing_keywords:
                    return self.huggingface.enhance_section_with_keywords(
                        section_content, missing_keywords
                    )
            except Exception as e:
                logger.error(f"Error enhancing {section_name} with HuggingFace: {str(e)}")
                
        # Basic enhancement
        # If skill section and we have missing keywords, add them
        if section_name.lower() == "skills" and "missing_keywords" in match_results:
            missing_skills = match_results["missing_keywords"][:5]  # Top 5 missing skills
            
            # Check if skills are already in section (case-insensitive)
            enhanced_content = section_content
            for skill in missing_skills:
                if not re.search(r'\b' + re.escape(skill) + r'\b', enhanced_content, re.IGNORECASE):
                    # Add skill with a "Familiar with" prefix to indicate it's added
                    if "•" in enhanced_content:
                        # If bullet points are used, add another bullet
                        enhanced_content += f"\n• Familiar with {skill}"
                    else:
                        # Otherwise, add with comma
                        enhanced_content += f", Familiar with {skill}"
                        
            return enhanced_content
            
        # For summary/objective, add job-specific language
        elif section_name.lower() in ["summary", "objective"]:
            # Extract job title if possible
            job_title_match = re.search(r'(job title|position)[:]*\s*([^,\n\.]+)', job_description, re.IGNORECASE)
            job_title = job_title_match.group(2).strip() if job_title_match else "the position"
            
            # Add job-specific statement if not already mentioned
            if job_title.lower() not in section_content.lower():
                return section_content + f"\n\nSeeking to leverage my skills and experience as {job_title}."
                
        # For other sections, return as is
        return section_content
        
    @st.cache_data(ttl=3600)  # Cache results for 1 hour
    def generate_cover_letter(self, resume_sections, job_description, company_name=None):
        """
        Generate a cover letter based on a resume and job description
        
        Args:
            resume_sections (dict): Dictionary of resume sections
            job_description (str): Job description text
            company_name (str, optional): Company name
            
        Returns:
            str: Generated cover letter
        """
        # Extract applicant name from personal information if available
        applicant_name = "Applicant"
        if "Personal Information" in resume_sections and resume_sections["Personal Information"] != "Missing":
            name_match = re.search(r'([A-Z][a-z]+ [A-Z][a-z]+)', resume_sections["Personal Information"])
            if name_match:
                applicant_name = name_match.group(1)
                
        # Extract job title from job description
        job_title = "the position"
        job_title_match = re.search(r'(job title|position)[:]*\s*([^,\n\.]+)', job_description, re.IGNORECASE)
        if job_title_match:
            job_title = job_title_match.group(2).strip()
            
        # Use company name if provided
        company = company_name or "your company"
        
        # If Gemini is available, use it to generate a personalized cover letter
        if self.gemini_available:
            try:
                # Create a condensed resume for the prompt
                resume_info = ""
                for section_name in ["Summary", "Skills", "Work Experience", "Education"]:
                    if section_name in resume_sections and resume_sections[section_name] != "Missing":
                        resume_info += f"{section_name}: {resume_sections[section_name]}\n\n"
                        
                prompt = f"""
                Write a professional cover letter for {applicant_name} applying for the {job_title} position at {company}.
                
                RESUME INFORMATION:
                ```
                {resume_info}
                ```
                
                JOB DESCRIPTION:
                ```
                {job_description}
                ```
                
                The cover letter should:
                1. Be approximately 3-4 paragraphs
                2. Start with a professional greeting
                3. Express enthusiasm for the position and company
                4. Highlight relevant skills and experiences that match the job requirements
                5. Demonstrate knowledge of the company (in generic terms)
                6. Include a call to action in the closing paragraph
                7. End with a professional sign-off
                
                Please provide ONLY the cover letter text with appropriate formatting.
                """
                
                cover_letter = self.gemini.generate_text(prompt, temperature=0.5)
                
                # Clean up any markdown code blocks or unnecessary text
                cover_letter = re.sub(r'```.*?\n', '', cover_letter)
                cover_letter = re.sub(r'```', '', cover_letter)
                
                return cover_letter.strip()
                
            except Exception as e:
                logger.error(f"Error generating cover letter with Gemini: {str(e)}")
                # Fall back to template
                
        # Template-based cover letter as fallback
        today = st.session_state.get("current_date", "Current Date")
        
        cover_letter = f"""
        {today}
        
        Dear Hiring Manager,
        
        I am writing to express my interest in the {job_title} position at {company}. With my background and skills, I believe I would be a valuable addition to your team.
        
        """
        
        # Add skills section if available
        if "Skills" in resume_sections and resume_sections["Skills"] != "Missing":
            skills_text = resume_sections["Skills"]
            # Extract first few skills
            skills = re.findall(r'(?:[\•\-]\s*|,\s*)([^,\n\•\-]+)', skills_text)[:3]
            if skills:
                skills_str = ", ".join(skills)
                cover_letter += f"My expertise in {skills_str}, along with my experience, makes me well-suited for this role. "
                
        # Add experience highlights if available
        if "Work Experience" in resume_sections and resume_sections["Work Experience"] != "Missing":
            cover_letter += "My professional experience has prepared me to excel in this position. "
            
        # Add education if available
        if "Education" in resume_sections and resume_sections["Education"] != "Missing":
            education_text = resume_sections["Education"]
            degree_match = re.search(r'(Bachelor|Master|PhD|MBA|Associate)', education_text, re.IGNORECASE)
            if degree_match:
                degree = degree_match.group(1)
                cover_letter += f"With my {degree}'s degree and relevant training, I am prepared to contribute immediately. "
                
        # Add closing
        cover_letter += """
        
        I am excited about the opportunity to join your team and contribute to your company's success. I would welcome the chance to discuss how my background, skills, and experience would be beneficial to your organization.
        
        Thank you for your time and consideration. I look forward to hearing from you soon.
        
        Sincerely,
        
        """
        
        cover_letter += applicant_name
        
        return cover_letter.strip() 