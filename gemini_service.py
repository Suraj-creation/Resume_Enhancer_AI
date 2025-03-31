"""
Gemini Service - Provides access to Google's Gemini AI capabilities
"""

import os
import time
import json
import re
import logging
import streamlit as st
from utils.api_config import API_CONFIG

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Lazy load Google generative AI to improve startup time
@st.cache_resource
def load_genai():
    try:
        import google.generativeai as genai
        return genai
    except ImportError:
        logger.error("Failed to import google.generativeai. Please install it with: pip install google-generativeai")
        return None

class GeminiService:
    """Service for interacting with Google's Gemini AI models"""
    
    def __init__(self, api_key=None):
        """
        Initialize the Gemini service
        
        Args:
            api_key (str, optional): Gemini API key. If not provided, 
                                     it will try to load from environment.
        """
        self.api_key = api_key or API_CONFIG["google_cloud"]["gemini_api_key"]
        if not self.api_key:
            print("ERROR: No Gemini API key provided or found in environment.")
            raise ValueError("Gemini API key is required")
            
        print(f"Initializing Gemini service with API key: {self.api_key[:5]}...")
        
        # Lazy load genai only when needed
        self.genai = load_genai()
        if not self.genai:
            print("ERROR: Google Generative AI package not found")
            raise ImportError("Google Generative AI package not available")
            
        try:
            # Configure the Gemini API
            self.genai.configure(api_key=self.api_key)
            
            # Store models as attributes to initialize them on first use
            self._model = None
            self._vision_model = None
            
            # Store conversations by user session
            self.conversations = {}
            print("Gemini service initialized successfully!")
        except Exception as e:
            print(f"ERROR initializing Gemini service: {str(e)}")
            raise
    
    @property
    def model(self):
        # Lazy initialization of model
        if self._model is None:
            self._model = self.genai.GenerativeModel('gemini-pro')
        return self._model
        
    @property
    def vision_model(self):
        # Lazy initialization of vision model
        if self._vision_model is None:
            self._vision_model = self.genai.GenerativeModel('gemini-pro-vision')
        return self._vision_model
        
    @st.cache_data(ttl=3600, show_spinner=False)  # Cache for 1 hour
    def generate_text(self, prompt, temperature=0.7, max_output_tokens=1024):
        """
        Generate text using Gemini Pro
        
        Args:
            prompt (str): The prompt to generate text from
            temperature (float): Controls randomness (0.0-1.0)
            max_output_tokens (int): Maximum number of tokens to generate
            
        Returns:
            str: Generated text
        """
        try:
            # Use a placeholder ID to ensure each unique prompt gets cached separately
            placeholder_id = hash(prompt + str(temperature) + str(max_output_tokens))
            st.session_state.setdefault('gemini_text_cache', {})
            
            # Check if we have a cached result
            if placeholder_id in st.session_state.gemini_text_cache:
                return st.session_state.gemini_text_cache[placeholder_id]
            
            response = self.model.generate_content(
                prompt,
                generation_config=self.genai.types.GenerationConfig(
                    temperature=temperature,
                    max_output_tokens=max_output_tokens,
                    top_p=0.95,
                    top_k=40
                )
            )
            
            result = response.text
            
            # Cache the result
            st.session_state.gemini_text_cache[placeholder_id] = result
            
            return result
            
        except Exception as e:
            logger.error(f"Error generating text with Gemini: {str(e)}")
            return f"Error: {str(e)}"
    
    @st.cache_data(ttl=3600, show_spinner=False)  # Cache for 1 hour
    def analyze_image(self, image_data, prompt):
        """
        Analyze an image using Gemini Pro Vision
        
        Args:
            image_data (bytes): Image data
            prompt (str): Prompt describing what to analyze in the image
            
        Returns:
            str: Analysis text
        """
        try:
            response = self.vision_model.generate_content(
                [prompt, image_data]
            )
            
            return response.text
            
        except Exception as e:
            logger.error(f"Error analyzing image with Gemini: {str(e)}")
            return f"Error: {str(e)}"
            
    @st.cache_data(ttl=3600, show_spinner=False)  # Cache for 1 hour
    def extract_resume_sections(self, resume_text):
        """
        Extract structured sections from a resume text
        
        Args:
            resume_text (str): The full text of the resume
            
        Returns:
            dict: Dictionary of resume sections
        """
        prompt = f"""
        As an AI resume analyzer, extract the following information from this resume text.
        For each section, return the content if present. If a section is not present, return "Missing".
        
        Sections to extract (be thorough and include ALL content for each section):
        1. Personal Information (name, email, phone, LinkedIn, GitHub, etc.)
        2. Summary/Objective (professional summary, career objective)
        3. Education (degrees, institutions, dates, GPA, relevant coursework)
        4. Skills (technical skills, soft skills, tools, technologies, programming languages)
        5. Work Experience (job titles, companies, dates, responsibilities, achievements)
        6. Projects (name, description, technologies used, outcomes)
        7. Certifications (name, issuing organization, dates)
        8. Awards (title, issuing organization, dates)
        9. Publications (title, journal/conference, date, co-authors)
        10. Languages (language name, proficiency level)
        
        The resume text is provided below:
        
        ```
        {resume_text}
        ```
        
        Format your response as a JSON object with section names as keys and content as values.
        If a section is missing, set its value to "Missing".
        """
        
        try:
            response = self.generate_text(prompt, temperature=0.1)
            
            # Try to parse JSON from the response
            try:
                # Extract JSON part if there's surrounding text
                if '{' in response and '}' in response:
                    json_str = response[response.find('{'):response.rfind('}')+1]
                    extracted_sections = json.loads(json_str)
                    return extracted_sections
            except json.JSONDecodeError:
                pass
            
            # If JSON parsing fails, return a simple structure with full text
            return {
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
            
        except Exception as e:
            logger.error(f"Error extracting resume sections: {str(e)}")
            # Return a default dictionary with the full text
            return {
                "full_text": resume_text,
                "error": str(e)
            }
            
    @st.cache_data(ttl=3600, show_spinner=False)  # Cache for 1 hour
    def match_resume_to_job(self, resume_sections, job_description):
        """
        Match resume against a job description and provide recommendations
        
        Args:
            resume_sections (dict): Dictionary of resume sections
            job_description (str): Job description text
            
        Returns:
            dict: Matching results and recommendations
        """
        # Create a single string with all resume content for analysis
        resume_text = "\n\n".join(
            f"{section}:\n{content}" 
            for section, content in resume_sections.items() 
            if content != "Missing" and section != "full_text"
        )
        
        prompt = f"""
        As an AI job matching expert, analyze this resume against the job description.
        
        RESUME:
        ```
        {resume_text}
        ```
        
        JOB DESCRIPTION:
        ```
        {job_description}
        ```
        
        Please provide:
        
        1. Match percentage (0-100) based on how well the resume matches the job requirements
        2. List of matching skills/qualifications found in both the resume and job description
        3. List of missing skills/qualifications that are in the job description but not in the resume
        4. Specific recommendations for tailoring the resume to better match this job
        
        Format your response as a JSON object with the following keys:
        - match_percentage: number between 0-100
        - matching_skills: array of strings
        - missing_skills: array of strings
        - recommendations: string with bullet points
        """
        
        try:
            response = self.generate_text(prompt, temperature=0.2)
            
            # Try to parse JSON from the response
            try:
                # Extract JSON part if there's surrounding text
                if '{' in response and '}' in response:
                    json_str = response[response.find('{'):response.rfind('}')+1]
                    match_results = json.loads(json_str)
                    return match_results
            except json.JSONDecodeError:
                pass
                
            # If JSON parsing fails, extract information using regex
            match_percentage_match = re.search(r'match_percentage["\s:]+(\d+)', response)
            match_percentage = int(match_percentage_match.group(1)) if match_percentage_match else 50
            
            matching_skills = re.findall(r'matching_skills["\s:]+\[(.*?)\]', response, re.DOTALL)
            matching_skills = matching_skills[0].split(',') if matching_skills else []
            
            missing_skills = re.findall(r'missing_skills["\s:]+\[(.*?)\]', response, re.DOTALL)
            missing_skills = missing_skills[0].split(',') if missing_skills else []
            
            recommendations_match = re.search(r'recommendations["\s:]+["\'](.*?)["\']', response, re.DOTALL)
            recommendations = recommendations_match.group(1) if recommendations_match else ""
            
            return {
                "match_percentage": match_percentage,
                "matching_skills": matching_skills,
                "missing_skills": missing_skills,
                "recommendations": recommendations
            }
            
        except Exception as e:
            logger.error(f"Error matching resume to job: {str(e)}")
            return {
                "match_percentage": 0,
                "matching_skills": [],
                "missing_skills": [],
                "recommendations": f"Error during analysis: {str(e)}"
            }
    
    @st.cache_data(ttl=3600, show_spinner=False)  # Cache results for 1 hour
    def enhance_resume_section(self, section_name, section_content, job_description=None):
        """
        Enhance a section of the resume, optionally tailoring it to a job description
        
        Args:
            section_name (str): Name of the section (e.g., summary, experience)
            section_content (str): Content of the section
            job_description (str, optional): Job description to tailor toward
            
        Returns:
            dict: Enhanced section content and suggestions
        """
        if not section_content or len(section_content.strip()) < 10:
            return {
                "enhanced_content": section_content,
                "suggestions": "Section content too short to enhance."
            }
        
        # Tailor prompt based on section
        section_specific_guidance = {
            "summary": "Focus on creating a concise professional summary that highlights key qualifications and achievements. Use powerful language and relevant keywords.",
            "experience": "Use strong action verbs, quantify achievements, and highlight relevant skills and technologies. Format consistently and focus on impact.",
            "education": "Present educational background clearly and concisely, highlighting relevant coursework, achievements, and credentials.",
            "skills": "Organize skills logically, prioritizing those most relevant to the target job. Include technical skills, soft skills, and proficiency levels.",
            "projects": "Highlight projects that demonstrate relevant skills, focusing on your role, technologies used, and measurable outcomes."
        }
        
        guidance = section_specific_guidance.get(
            section_name.lower(), 
            "Improve this section with clear, concise language and relevant details."
        )
        
        if job_description:
            prompt = f"""
            As an expert resume writer, enhance this {section_name} section to match the job description.
            
            CURRENT CONTENT:
            ```
            {section_content}
            ```
            
            JOB DESCRIPTION:
            ```
            {job_description}
            ```
            
            GUIDANCE:
            {guidance}
            
            Use only factual information present in the original content, but improve wording, structure, and relevance.
            
            Return your response as a JSON object with:
            - enhanced_content: The improved section content
            - suggestions: Brief explanation of improvements made
            """
        else:
            prompt = f"""
            As an expert resume writer, enhance this {section_name} section.
            
            CURRENT CONTENT:
            ```
            {section_content}
            ```
            
            GUIDANCE:
            {guidance}
            
            Use only factual information present in the original content, but improve wording, structure, and impact.
            
            Return your response as a JSON object with:
            - enhanced_content: The improved section content
            - suggestions: Brief explanation of improvements made
            """
        
        try:
            response = self.generate_text(prompt, temperature=0.3)
            
            # Try to parse JSON from the response
            try:
                if '{' in response and '}' in response:
                    json_str = response[response.find('{'):response.rfind('}')+1]
                    enhanced = json.loads(json_str)
                    return enhanced
            except json.JSONDecodeError:
                pass
            
            # If parsing fails, try to extract parts
            enhanced_content_match = re.search(r'enhanced_content["\s:]+["\'](.*?)["\']', response, re.DOTALL)
            enhanced_content = enhanced_content_match.group(1) if enhanced_content_match else section_content
            
            suggestions_match = re.search(r'suggestions["\s:]+["\'](.*?)["\']', response, re.DOTALL)
            suggestions = suggestions_match.group(1) if suggestions_match else "Content enhanced for clarity and impact."
            
            return {
                "enhanced_content": enhanced_content or section_content,
                "suggestions": suggestions
            }
            
        except Exception as e:
            logger.error(f"Error enhancing resume section: {str(e)}")
            return {
                "enhanced_content": section_content,
                "suggestions": f"Error during enhancement: {str(e)}"
            }
    
    @st.cache_data(ttl=3600, show_spinner=False)  # Cache results for 1 hour
    def generate_tailored_resume(self, resume_sections, job_description):
        """
        Generate a tailored version of the entire resume for a specific job
        
        Args:
            resume_sections (dict): Dictionary of resume sections
            job_description (str): Job description to tailor toward
            
        Returns:
            dict: Tailored resume sections
        """
        # Skip processing if no job description provided
        if not job_description or len(job_description.strip()) < 20:
            return resume_sections
            
        tailored_sections = {}
        
        # Process each section individually to avoid large API calls
        for section_name, content in resume_sections.items():
            # Skip empty sections or full_text
            if section_name == "full_text" or not content or content == "Missing":
                tailored_sections[section_name] = content
                continue
                
            # Enhance each section
            result = self.enhance_resume_section(section_name, content, job_description)
            tailored_sections[section_name] = result.get("enhanced_content", content)
            
        return tailored_sections
    
    @st.cache_data(ttl=3600, show_spinner=False)  # Cache results for 1 hour
    def check_grammar(self, text):
        """
        Check text for grammar and style issues
        
        Args:
            text (str): Text to check
            
        Returns:
            dict: Dictionary with grammar issues and overall assessment
        """
        if not text or len(text.strip()) < 20:
            return {
                "issues": [],
                "overall_assessment": "Text too short to analyze"
            }
            
        prompt = f"""
        As a professional editor, review the following text for grammar, style, and clarity issues.
        
        TEXT:
        ```
        {text}
        ```
        
        For each issue you find, provide:
        1. The problematic text
        2. The correction
        3. Brief explanation of the issue
        
        Also provide an overall assessment of the writing quality.
        
        Format your response as a JSON object with:
        - issues: Array of objects, each with "text", "correction", and "reason" fields
        - overall_assessment: Brief overall assessment of the writing
        """
        
        try:
            response = self.generate_text(prompt, temperature=0.1)
            
            # Try to parse JSON
            try:
                if '{' in response and '}' in response:
                    json_str = response[response.find('{'):response.rfind('}')+1]
                    result = json.loads(json_str)
                    return result
            except json.JSONDecodeError:
                pass
                
            # If parsing fails, extract information using regex
            issues = []
            issues_matches = re.findall(r'text["\s:]+["\'](.*?)["\'].*?correction["\s:]+["\'](.*?)["\']', response, re.DOTALL)
            
            for match in issues_matches:
                if len(match) >= 2:
                    issues.append({
                        "text": match[0],
                        "correction": match[1],
                        "reason": "Grammar or style issue"
                    })
                    
            assessment_match = re.search(r'overall_assessment["\s:]+["\'](.*?)["\']', response, re.DOTALL)
            assessment = assessment_match.group(1) if assessment_match else "No detailed assessment provided"
            
            return {
                "issues": issues,
                "overall_assessment": assessment
            }
            
        except Exception as e:
            logger.error(f"Error checking grammar: {str(e)}")
            return {
                "issues": [],
                "overall_assessment": f"Error during analysis: {str(e)}"
            }
    
    @st.cache_data(ttl=3600, show_spinner=False)  # Cache results for 1 hour
    def analyze_section_quality(self, section_name, section_content):
        """
        Analyze the quality of a specific resume section
        
        Args:
            section_name (str): Name of the section (e.g., summary, experience)
            section_content (str): Content of the section
            
        Returns:
            dict: Analysis with strengths, weaknesses, and suggestions
        """
        if not section_content or len(section_content.strip()) < 20:
            return {
                "strengths": "Section too short to analyze",
                "weaknesses": "Content insufficient for analysis",
                "suggestions": "Add more content to this section"
            }
            
        prompt = f"""
        As a professional resume reviewer, analyze this {section_name} section.
        
        SECTION CONTENT:
        ```
        {section_content}
        ```
        
        Provide a thorough analysis with:
        1. Strengths: What works well in this section
        2. Weaknesses: What could be improved
        3. Specific suggestions: Actionable recommendations for enhancement
        
        Format your response as a JSON object with:
        - strengths: String listing strengths, as bullet points
        - weaknesses: String listing weaknesses, as bullet points
        - suggestions: String with specific suggestions, as bullet points
        """
        
        try:
            response = self.generate_text(prompt, temperature=0.2)
            
            # Try to parse JSON
            try:
                if '{' in response and '}' in response:
                    json_str = response[response.find('{'):response.rfind('}')+1]
                    result = json.loads(json_str)
                    return result
            except json.JSONDecodeError:
                pass
                
            # If parsing fails, extract sections using regex
            strengths_match = re.search(r'strengths["\s:]+["\'](.*?)["\']', response, re.DOTALL)
            strengths = strengths_match.group(1) if strengths_match else "No specific strengths identified"
            
            weaknesses_match = re.search(r'weaknesses["\s:]+["\'](.*?)["\']', response, re.DOTALL)
            weaknesses = weaknesses_match.group(1) if weaknesses_match else "No specific weaknesses identified"
            
            suggestions_match = re.search(r'suggestions["\s:]+["\'](.*?)["\']', response, re.DOTALL)
            suggestions = suggestions_match.group(1) if suggestions_match else "No specific suggestions provided"
            
            return {
                "strengths": strengths,
                "weaknesses": weaknesses,
                "suggestions": suggestions
            }
            
        except Exception as e:
            logger.error(f"Error analyzing section quality: {str(e)}")
            return {
                "strengths": "Error during analysis",
                "weaknesses": "Unable to complete analysis",
                "suggestions": f"Error: {str(e)}"
            }
    
    @st.cache_data(ttl=3600, show_spinner=False)  # Cache results for 1 hour
    def extract_keywords_from_job(self, job_description):
        """
        Extract relevant keywords from a job description
        
        Args:
            job_description (str): Job description text
            
        Returns:
            list: List of extracted keywords
        """
        if not job_description or len(job_description.strip()) < 50:
            return []
            
        prompt = f"""
        As a keyword extraction expert, identify the most important keywords from this job description.
        Focus on skills, qualifications, tools, technologies, and industry terms that would be relevant for a resume.
        
        JOB DESCRIPTION:
        ```
        {job_description}
        ```
        
        Return ONLY a JSON array of strings with the 20 most important keywords, without any explanations.
        """
        
        try:
            response = self.generate_text(prompt, temperature=0.1)
            
            # Try to parse JSON
            try:
                # Look for array pattern
                array_match = re.search(r'\[(.*?)\]', response, re.DOTALL)
                if array_match:
                    keywords_json = f"[{array_match.group(1)}]"
                    keywords = json.loads(keywords_json)
                    return keywords
            except json.JSONDecodeError:
                pass
                
            # If JSON parsing fails, try to extract keywords using regex
            keywords = re.findall(r'["\'](.*?)["\']', response)
            return keywords[:20]  # Limit to 20 keywords
            
        except Exception as e:
            logger.error(f"Error extracting keywords: {str(e)}")
            return [] 