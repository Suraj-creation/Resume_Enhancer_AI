"""
Resume Analyzer Service - Provides AI-powered resume analysis capabilities
"""

import logging
import streamlit as st
from typing import Dict, List, Any, Optional, Union
import re

from utils.ai_services.service_manager import AIServiceManager

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ResumeAnalyzerService:
    """Service for analyzing resumes using AI"""
    
    def __init__(self, api_key=None):
        """
        Initialize the Resume Analyzer service
        
        Args:
            api_key (str, optional): Not used directly, but kept for API compatibility
        """
        # Get the service manager
        self.service_manager = AIServiceManager()
        
        # Try to get Gemini service
        self.gemini = self.service_manager.get_service("gemini")
        
        # Try to get HuggingFace service
        self.huggingface = self.service_manager.get_service("huggingface")
        
        # Set availability flags
        self.gemini_available = self.gemini is not None
        self.huggingface_available = self.huggingface is not None
        
    def extract_resume_sections(self, resume_text):
        """
        Extract structured sections from a resume text
        
        Args:
            resume_text (str): The full text of the resume
            
        Returns:
            dict: Dictionary of resume sections
        """
        if self.gemini_available:
            try:
                return self.gemini.extract_resume_sections(resume_text)
            except Exception as e:
                logger.error(f"Error extracting resume sections with Gemini: {str(e)}")
                # Fall back to basic extraction
                
        # Basic section extraction based on common section headers
        sections = {
            "full_text": resume_text,
            "Personal Information": "Missing",
            "Summary": "Missing",
            "Education": "Missing",
            "Skills": "Missing",
            "Work Experience": "Missing",
            "Projects": "Missing",
            "Certifications": "Missing",
            "Awards": "Missing",
            "Publications": "Missing",
            "Languages": "Missing"
        }
        
        # Look for common section headers
        section_patterns = {
            "Personal Information": r"(?:PERSONAL\s+INFORMATION|CONTACT|PERSONAL\s+DETAILS)",
            "Summary": r"(?:SUMMARY|PROFILE|OBJECTIVE|PROFESSIONAL\s+SUMMARY|CAREER\s+OBJECTIVE)",
            "Education": r"(?:EDUCATION|ACADEMIC|EDUCATIONAL\s+BACKGROUND|ACADEMIC\s+BACKGROUND)",
            "Skills": r"(?:SKILLS|TECHNICAL\s+SKILLS|CORE\s+COMPETENCIES|COMPETENCIES|EXPERTISE)",
            "Work Experience": r"(?:WORK\s+EXPERIENCE|EXPERIENCE|PROFESSIONAL\s+EXPERIENCE|EMPLOYMENT|WORK\s+HISTORY)",
            "Projects": r"(?:PROJECTS|PROJECT\s+EXPERIENCE|RELEVANT\s+PROJECTS)",
            "Certifications": r"(?:CERTIFICATIONS|CERTIFICATES|PROFESSIONAL\s+CERTIFICATIONS)",
            "Awards": r"(?:AWARDS|HONORS|ACHIEVEMENTS|RECOGNITIONS)",
            "Publications": r"(?:PUBLICATIONS|PAPERS|RESEARCH|ARTICLES)",
            "Languages": r"(?:LANGUAGES|LANGUAGE\s+SKILLS)"
        }
        
        for section_name, pattern in section_patterns.items():
            # Find all occurrences of the pattern
            matches = re.finditer(pattern, resume_text, re.IGNORECASE)
            
            for match in matches:
                # Get start position of the section
                start_pos = match.end()
                
                # Find the next section header to determine end position
                end_pos = len(resume_text)
                for next_pattern in section_patterns.values():
                    next_match = re.search(next_pattern, resume_text[start_pos:], re.IGNORECASE)
                    if next_match:
                        next_start = next_match.start() + start_pos
                        if next_start < end_pos:
                            end_pos = next_start
                
                # Extract section content
                section_content = resume_text[start_pos:end_pos].strip()
                
                # Only update if it's missing or if we found a non-empty section
                if sections[section_name] == "Missing" and section_content:
                    sections[section_name] = section_content
                    
        return sections
        
    def analyze_resume_quality(self, resume_sections):
        """
        Analyze the quality of a resume and provide detailed feedback
        
        Args:
            resume_sections (dict): Dictionary of resume sections
            
        Returns:
            dict: Quality analysis results
        """
        # Initialize results structure
        results = {
            "overall_score": 0,
            "section_scores": {},
            "strengths": [],
            "weaknesses": [],
            "improvement_suggestions": []
        }
        
        # Check if HuggingFace is available for scoring
        if self.huggingface_available:
            try:
                hf_score = self.huggingface.score_resume(resume_sections)
                results["overall_score"] = hf_score.get("score", 50)
                results["strengths"].extend(hf_score.get("strengths", []))
                results["improvement_suggestions"].extend(hf_score.get("improvements", []))
            except Exception as e:
                logger.error(f"Error scoring resume with HuggingFace: {str(e)}")
                # Fall back to Gemini
                
        # If no score yet or HuggingFace failed, try Gemini
        if results["overall_score"] == 0 and self.gemini_available:
            # Analyze each section individually
            section_scores = {}
            all_strengths = []
            all_weaknesses = []
            all_recommendations = []
            
            for section_name, content in resume_sections.items():
                if section_name == "full_text" or content == "Missing":
                    continue
                
                try:
                    analysis = self.gemini.analyze_section_quality(section_name, content)
                    
                    # Store section score
                    section_scores[section_name] = analysis.get("score", 0)
                    
                    # Collect strengths, weaknesses, and recommendations
                    all_strengths.extend(analysis.get("strengths", []))
                    all_weaknesses.extend(analysis.get("weaknesses", []))
                    all_recommendations.extend(analysis.get("recommendations", []))
                    
                except Exception as e:
                    logger.error(f"Error analyzing {section_name} section: {str(e)}")
                    
            # Calculate overall score (average of section scores)
            if section_scores:
                overall_score = sum(section_scores.values()) / len(section_scores)
                results["overall_score"] = int(overall_score)
                
            # Update section scores and feedback
            results["section_scores"] = section_scores
            results["strengths"] = all_strengths[:5]  # Limit to top 5
            results["weaknesses"] = all_weaknesses[:5]  # Limit to top 5
            results["improvement_suggestions"] = all_recommendations[:7]  # Limit to top 7
            
        # If we still don't have an overall score, use a basic calculation
        if results["overall_score"] == 0:
            # Basic scoring based on presence and length of sections
            section_scores = {}
            for section_name, content in resume_sections.items():
                if section_name == "full_text":
                    continue
                    
                if content == "Missing":
                    section_scores[section_name] = 0
                else:
                    # Score based on length (adjust thresholds as needed)
                    length = len(content)
                    if length < 50:
                        section_scores[section_name] = 30
                    elif length < 200:
                        section_scores[section_name] = 60
                    else:
                        section_scores[section_name] = 80
                        
            # Calculate overall score
            overall_score = sum(section_scores.values()) / len(section_scores)
            results["overall_score"] = int(overall_score)
            results["section_scores"] = section_scores
            
            # Add generic improvement suggestions
            results["improvement_suggestions"] = [
                "Add missing sections to your resume",
                "Provide more detailed information for each section",
                "Use bullet points to highlight achievements",
                "Include quantifiable results and metrics",
                "Ensure your resume is tailored to your target industry"
            ]
            
        return results
        
    def extract_keywords(self, resume_sections):
        """
        Extract important keywords from a resume
        
        Args:
            resume_sections (dict): Dictionary of resume sections
            
        Returns:
            dict: Dictionary with extracted keywords
        """
        # Create a single string with relevant sections
        resume_text = ""
        for section_name, content in resume_sections.items():
            if section_name not in ["full_text", "_match_results"] and content != "Missing":
                resume_text += f"{content}\n\n"
                
        # Define common keyword categories
        keyword_categories = {
            "technical_skills": [
                "python", "java", "javascript", "c++", "c#", "ruby", "php", "html", "css",
                "react", "angular", "vue", "node.js", "django", "flask", "spring", "express",
                "aws", "azure", "gcp", "cloud", "docker", "kubernetes", "devops", "ci/cd",
                "machine learning", "ai", "artificial intelligence", "data science", "analytics",
                "sql", "nosql", "database", "mongodb", "mysql", "postgresql", "oracle",
                "tensorflow", "pytorch", "scikit-learn", "nlp", "natural language processing",
                "tableau", "power bi", "excel", "data visualization", "git", "github"
            ],
            "soft_skills": [
                "leadership", "communication", "teamwork", "collaboration", "problem solving",
                "critical thinking", "time management", "project management", "agile", "scrum",
                "customer service", "interpersonal", "adaptability", "flexibility", "creativity",
                "attention to detail", "organization", "multitasking", "negotiation", "presentation"
            ],
            "education": [
                "bachelor", "master", "phd", "doctorate", "mba", "degree", "university",
                "college", "gpa", "honors", "cum laude", "magna cum laude", "summa cum laude",
                "certification", "diploma", "thesis", "dissertation", "coursework", "graduate"
            ],
            "experience": [
                "years of experience", "led", "managed", "developed", "implemented", "designed",
                "created", "launched", "optimized", "improved", "increased", "decreased",
                "reduced", "achieved", "delivered", "supervised", "coordinated", "analyzed",
                "budget", "revenue", "profit", "team", "stakeholders", "clients", "customers"
            ]
        }
        
        # Initialize results
        results = {
            "extracted_keywords": {},
            "top_keywords": []
        }
        
        # Extract keywords for each category
        for category, keywords in keyword_categories.items():
            category_matches = {}
            
            for keyword in keywords:
                # Count occurrences (case-insensitive)
                count = len(re.findall(r'\b' + re.escape(keyword) + r'\b', resume_text.lower()))
                if count > 0:
                    category_matches[keyword] = count
                    
            # Sort by count (descending)
            sorted_matches = dict(sorted(category_matches.items(), key=lambda x: x[1], reverse=True))
            results["extracted_keywords"][category] = sorted_matches
            
            # Add top keywords to the overall list
            top_n = list(sorted_matches.keys())[:5]  # Top 5 from each category
            results["top_keywords"].extend(top_n)
            
        # If HuggingFace is available, use it to enhance keyword extraction
        if self.huggingface_available:
            try:
                # Use zero-shot classification to categorize text
                section_labels = ["technical", "leadership", "business", "communication", "analytical"]
                
                for section_name, content in resume_sections.items():
                    if section_name in ["full_text", "_match_results"] or content == "Missing":
                        continue
                        
                    # Classify section content
                    classification = self.huggingface.zero_shot_classification(content, section_labels)
                    
                    # Get top label
                    if "labels" in classification and "scores" in classification:
                        top_label = classification["labels"][0]
                        score = classification["scores"][0]
                        
                        # If high confidence, add to results
                        if score > 0.7:
                            results["section_classifications"] = results.get("section_classifications", {})
                            results["section_classifications"][section_name] = {
                                "primary_category": top_label,
                                "confidence": score
                            }
                            
            except Exception as e:
                logger.error(f"Error enhancing keyword extraction with HuggingFace: {str(e)}")
                
        return results
        
    def match_to_job(self, resume_sections, job_description):
        """
        Match a resume against a job description
        
        Args:
            resume_sections (dict): Dictionary of resume sections
            job_description (str): Job description text
            
        Returns:
            dict: Matching results and recommendations
        """
        # Try Gemini first for comprehensive matching
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
        
    def enhance_resume_section(self, section_name, section_content, job_description=None):
        """
        Enhance a resume section with improved content and formatting
        
        Args:
            section_name (str): Name of the section (e.g., "Skills", "Work Experience")
            section_content (str): Current content of the section
            job_description (str, optional): Job description to tailor section towards
            
        Returns:
            str: Enhanced section content
        """
        # Try Gemini first for best enhancement
        if self.gemini_available:
            try:
                enhanced_content = self.gemini.enhance_resume_section(
                    section_name, section_content, job_description
                )
                return enhanced_content
            except Exception as e:
                logger.error(f"Error enhancing section with Gemini: {str(e)}")
                # Fall back to HuggingFace or basic enhancement
                
        # If Gemini failed or is not available, try simple enhancement with HuggingFace
        if self.huggingface_available and job_description:
            try:
                # Extract keywords from job description to incorporate
                match_result = self.huggingface.match_resume_to_job(
                    {section_name: section_content}, job_description
                )
                
                target_keywords = match_result.get("missing_keywords", [])[:5]
                
                # Enhance with keywords
                if target_keywords:
                    return self.huggingface.enhance_section_with_keywords(
                        section_content, target_keywords
                    )
                    
            except Exception as e:
                logger.error(f"Error enhancing section with HuggingFace: {str(e)}")
                
        # Return original content if enhancement failed
        return section_content
        
    def generate_tailored_resume(self, resume_sections, job_description):
        """
        Generate a fully tailored resume based on a job description
        
        Args:
            resume_sections (dict): Dictionary of resume sections
            job_description (str): Job description text
            
        Returns:
            dict: Dictionary of tailored resume sections
        """
        # Get match results first
        match_results = self.match_to_job(resume_sections, job_description)
        
        # If Gemini is available, use it for comprehensive tailoring
        if self.gemini_available:
            try:
                tailored_sections = self.gemini.generate_tailored_resume(
                    resume_sections, job_description
                )
                return tailored_sections
            except Exception as e:
                logger.error(f"Error generating tailored resume with Gemini: {str(e)}")
                # Fall back to section-by-section enhancement
                
        # Enhance each section individually
        tailored_sections = {}
        
        for section_name, content in resume_sections.items():
            # Skip full_text or missing sections
            if section_name == "full_text" or content == "Missing":
                tailored_sections[section_name] = content
                continue
                
            # Enhance the section
            tailored_sections[section_name] = self.enhance_resume_section(
                section_name, content, job_description
            )
            
        # Add match results for reference
        tailored_sections["_match_results"] = match_results
        
        return tailored_sections
        
    @st.cache_data(ttl=3600)  # Cache results for 1 hour
    def extract_entities_from_resume(self, resume_sections):
        """
        Extract named entities from a resume
        
        Args:
            resume_sections (dict): Dictionary of resume sections
            
        Returns:
            dict: Dictionary of entities by type
        """
        if not self.huggingface_available:
            return {"error": "HuggingFace service not available"}
            
        # Create a single string from all sections
        resume_text = ""
        for section_name, content in resume_sections.items():
            if section_name not in ["full_text", "_match_results"] and content != "Missing":
                resume_text += f"{content}\n\n"
                
        try:
            # Extract entities
            entities = self.huggingface.extract_named_entities(resume_text)
            
            # Group by entity type
            entities_by_type = {}
            for entity in entities:
                entity_type = entity.get("entity", "OTHER")
                entity_word = entity.get("word", "")
                
                if entity_type not in entities_by_type:
                    entities_by_type[entity_type] = []
                    
                if entity_word and entity_word not in entities_by_type[entity_type]:
                    entities_by_type[entity_type].append(entity_word)
                    
            return entities_by_type
            
        except Exception as e:
            logger.error(f"Error extracting entities: {str(e)}")
            return {"error": str(e)}
            
    @st.cache_data(ttl=3600)  # Cache results for 1 hour
    def summarize_resume(self, resume_sections, max_length=150):
        """
        Generate a concise summary of a resume
        
        Args:
            resume_sections (dict): Dictionary of resume sections
            max_length (int): Maximum summary length
            
        Returns:
            str: Resume summary
        """
        # If both Gemini and HuggingFace are unavailable, use the existing summary
        if not self.gemini_available and not self.huggingface_available:
            if "Summary" in resume_sections and resume_sections["Summary"] != "Missing":
                return resume_sections["Summary"]
            return "No summary available."
            
        # Create a condensed version of the resume for input
        resume_text = ""
        
        # Add existing summary if available
        if "Summary" in resume_sections and resume_sections["Summary"] != "Missing":
            resume_text += f"Summary: {resume_sections['Summary']}\n\n"
            
        # Add key sections
        for section_name in ["Education", "Skills", "Work Experience"]:
            if section_name in resume_sections and resume_sections[section_name] != "Missing":
                resume_text += f"{section_name}: {resume_sections[section_name]}\n\n"
                
        # Try Gemini first for well-structured summary
        if self.gemini_available:
            try:
                prompt = f"""
                Create a concise professional summary for a resume based on the following information.
                
                RESUME CONTENT:
                ```
                {resume_text}
                ```
                
                The summary should:
                1. Be approximately 3-4 sentences (max 150 words)
                2. Highlight key skills, experience, and qualifications
                3. Be written in a professional first-person style
                4. Focus on strengths and value proposition
                
                Please provide ONLY the summary text with no additional explanation.
                """
                
                summary = self.gemini.generate_text(prompt, temperature=0.3)
                
                # Clean up any markdown code blocks or unnecessary text
                summary = re.sub(r'```.*?\n', '', summary)
                summary = re.sub(r'```', '', summary)
                
                return summary.strip()
                
            except Exception as e:
                logger.error(f"Error generating summary with Gemini: {str(e)}")
                # Fall back to HuggingFace
                
        # If Gemini failed or is not available, try HuggingFace
        if self.huggingface_available:
            try:
                return self.huggingface.summarize_text(resume_text, max_length=max_length, min_length=30)
            except Exception as e:
                logger.error(f"Error generating summary with HuggingFace: {str(e)}")
                
        # If both failed, return a generic message
        return "Unable to generate summary. Please try again later." 