import os
import time
import json
import google.generativeai as genai
from dotenv import load_dotenv
import streamlit as st
import re
from utils.api_config import API_CONFIG

# Load environment variables
load_dotenv()

def analyze_text_with_gemini(text, analysis_type="resume"):
    """
    Analyze text using the Gemini API
    
    Args:
        text (str): The text to analyze
        analysis_type (str): Type of analysis to perform (e.g., 'resume', 'cover_letter')
        
    Returns:
        dict: Analysis results
    """
    try:
        client = create_gemini_client()
        
        if analysis_type == "resume":
            # For resume analysis, extract structured data
            return client.extract_resume_sections(text)
        elif analysis_type == "grammar":
            # For grammar analysis, check for issues
            return check_grammar_with_gemini(text, client)
        else:
            # Default general analysis
            return general_text_analysis(text, client)
    except Exception as e:
        st.error(f"Error analyzing text with Gemini: {str(e)}")
        # Return a default empty result
        return {
            "analysis_result": "Analysis failed",
            "error": str(e)
        }

def check_grammar_with_gemini(text, client):
    """
    Check grammar in text using Gemini
    
    Args:
        text (str): Text to check
        client: Gemini client instance
        
    Returns:
        dict: Grammar analysis results
    """
    prompt = f"""
    Analyze the following text for grammar, spelling, and style issues.
    Identify specific errors and provide corrections.
    
    Text to analyze:
    ```
    {text}
    ```
    
    Format your response as a JSON object with:
    1. "issues": A list of objects, each containing "text" (the problematic text), 
                "correction" (suggested correction), and "type" (grammar/spelling/style)
    2. "overall_assessment": A brief assessment of the writing quality
    """
    
    try:
        response = client._make_api_call_with_retry(prompt)
        
        # Try to extract JSON from the response
        json_match = re.search(r'({.*})', response.replace('\n', ' '), re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass
        
        # Fallback to basic response
        return {
            "issues": [],
            "overall_assessment": "Grammar analysis unavailable"
        }
    except Exception as e:
        print(f"Grammar check error: {str(e)}")
        return {
            "issues": [],
            "overall_assessment": "Grammar analysis failed"
        }

def general_text_analysis(text, client):
    """
    Perform general analysis on text using Gemini
    
    Args:
        text (str): Text to analyze
        client: Gemini client instance
        
    Returns:
        dict: Analysis results
    """
    prompt = f"""
    Analyze the following text and provide insights:
    1. Key topics and themes
    2. Tone and writing style
    3. Areas for improvement
    
    Text to analyze:
    ```
    {text}
    ```
    
    Format your response as a JSON object with keys for each analysis area.
    """
    
    try:
        response = client._make_api_call_with_retry(prompt)
        
        # Try to extract JSON from the response
        json_match = re.search(r'({.*})', response.replace('\n', ' '), re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass
        
        # Fallback to basic response
        return {
            "analysis": response,
            "format": "text"
        }
    except Exception as e:
        print(f"Text analysis error: {str(e)}")
        return {
            "analysis": "Analysis failed",
            "error": str(e)
        }

def create_gemini_client():
    """
    Create and return a GeminiProcessor instance
    """
    # Configure Gemini API with the API key from environment variables
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY must be set in environment variables")
    
    genai.configure(api_key=api_key)
    return GeminiProcessor()

class GeminiProcessor:
    """Class to handle all interactions with the Gemini API"""
    
    def __init__(self):
        """Initialize the GeminiProcessor with the Gemini Pro model"""
        self.model = genai.GenerativeModel('gemini-pro')
        self.history = {}  # Store conversation history for each user
    
    def extract_resume_sections(self, resume_text):
        """
        Extract key sections from a resume with enhanced parsing
        
        Args:
            resume_text: The text content of the resume
        
        Returns:
            dict: Dictionary with extracted sections
        """
        # Create a more detailed prompt for better extraction
        prompt = f"""
        As an AI resume analyzer, extract the following information from this resume text.
        For each section, return the content if present. If a section is not present, return "Missing".
        
        Sections to extract (be thorough and include ALL content for each section):
        1. Personal Information (name, email, phone, LinkedIn, GitHub, etc.)
        2. Objective/Resume Summary (professional summary, career objective)
        3. Education (degrees, institutions, dates, GPA, relevant coursework)
        4. Skills (technical skills, soft skills, tools, technologies, programming languages)
        5. Work Experience (job titles, companies, dates, responsibilities, achievements)
        6. Certifications (name, issuing organization, dates)
        7. Projects (name, description, technologies used, outcomes)
        8. Awards and Honors (title, issuing organization, dates)
        9. Publications (title, journal/conference, date, co-authors)
        10. Languages (language name, proficiency level)
        11. Professional Affiliations (organization names, roles, dates)
        
        Be comprehensive in extracting full content for each section. Make sure to preserve all details, including:
        - Dates and durations
        - Numeric achievements (e.g., "increased efficiency by 35%")
        - Technical terms and acronyms
        - All bullet points from experience or project descriptions
        
        The resume text is provided below:
        
        ```
        {resume_text}
        ```
        
        For each section, provide only the content, not the section name. 
        Format your response as a JSON object with section names as keys and content as values.
        If a section is missing, set its value to "Missing".
        """
        
        try:
            # Make the API call with retry mechanism for robustness
            response = self._make_api_call_with_retry(prompt)
            
            # Try to parse JSON response first
            try:
                # Check if response is already in JSON format
                if '{' in response and '}' in response:
                    # Extract JSON part if there's surrounding text
                    json_str = response[response.find('{'):response.rfind('}')+1]
                    extracted_sections = json.loads(json_str)
                    
                    # Convert keys to standard format if needed
                    standardized_sections = {}
                    key_mapping = {
                        "personal information": "Personal Information",
                        "objective": "Objective",
                        "summary": "Objective",
                        "resume summary": "Objective",
                        "education": "Education",
                        "skills": "Skills",
                        "work experience": "Work Experience",
                        "experience": "Work Experience",
                        "certifications": "Certifications",
                        "projects": "Projects",
                        "awards and honors": "Awards and Honors",
                        "awards": "Awards and Honors",
                        "honors": "Awards and Honors",
                        "publications": "Publications",
                        "languages": "Languages",
                        "professional affiliations": "Professional Affiliations"
                    }
                    
                    for key, value in extracted_sections.items():
                        # Find the standardized key
                        std_key = None
                        for k, v in key_mapping.items():
                            if k.lower() in key.lower():
                                std_key = v
                                break
                        
                        # If no matching standard key, use the original
                        if not std_key:
                            std_key = key
                        
                        standardized_sections[std_key] = value
                    
                    return standardized_sections
            except json.JSONDecodeError:
                # If JSON parsing fails, fall back to text parsing
                pass
            
            # Fallback: Text-based parsing
            extracted_sections = {
                "Personal Information": "Missing",
                "Objective": "Missing",
                "Education": "Missing",
                "Skills": "Missing",
                "Work Experience": "Missing",
                "Certifications": "Missing",
                "Projects": "Missing",
                "Awards and Honors": "Missing",
                "Publications": "Missing",
                "Languages": "Missing",
                "Professional Affiliations": "Missing"
            }
            
            # Parse the response text
            current_section = None
            section_content = ""
            
            section_starters = {
                "personal information": "Personal Information",
                "objective": "Objective",
                "summary": "Objective",
                "education": "Education",
                "skills": "Skills",
                "work experience": "Work Experience",
                "experience": "Work Experience",
                "certifications": "Certifications",
                "projects": "Projects",
                "awards": "Awards and Honors",
                "honors": "Awards and Honors",
                "publications": "Publications",
                "languages": "Languages",
                "professional affiliations": "Professional Affiliations"
            }
            
            for line in response.split("\n"):
                line = line.strip()
                if not line:
                    continue
                
                # Check if line starts a new section
                new_section = None
                for starter, section in section_starters.items():
                    if line.lower().startswith(starter) and ":" in line:
                        new_section = section
                        break
                
                if new_section:
                    # Save previous section
                    if current_section and section_content:
                        extracted_sections[current_section] = section_content.strip()
                    
                    # Start new section
                    current_section = new_section
                    section_content = line.split(":", 1)[1].strip() if ":" in line else ""
                elif current_section:
                    section_content += "\n" + line
            
            # Save the last section
            if current_section and section_content:
                extracted_sections[current_section] = section_content.strip()
            
            return extracted_sections
            
        except Exception as e:
            print(f"Error extracting resume sections: {str(e)}")
            # Return empty sections on error
            return {
                "Personal Information": "Missing",
                "Objective": "Missing",
                "Education": "Missing",
                "Skills": "Missing",
                "Work Experience": "Missing",
                "Certifications": "Missing",
                "Projects": "Missing",
                "Awards and Honors": "Missing",
                "Publications": "Missing",
                "Languages": "Missing",
                "Professional Affiliations": "Missing"
            }
    
    def calculate_resume_scores(self, resume_sections):
        """
        Calculate GenAI and AI scores based on resume content with enhanced analysis
        
        Args:
            resume_sections: Dictionary with extracted resume sections
        
        Returns:
            dict: Dictionary with detailed GenAI and AI scores
        """
        # Convert resume sections to a string representation for the prompt
        resume_content = "\n\n".join([f"{key}:\n{value}" for key, value in resume_sections.items() if value != "Missing"])
        
        prompt = f"""
        Perform a comprehensive evaluation of this resume for relevance to GenAI and AI fields.
        
        GenAI Score (0-100) should assess:
        - Presence and depth of Generative AI terms and concepts (GANs, VAEs, diffusion models, transformers)
        - LLM experience (GPT, BERT, fine-tuning, prompt engineering)
        - Relevant tools and frameworks (PyTorch, Hugging Face, Stable Diffusion)
        - Associated concepts (synthetic data generation, model interpretability)
        - Level of hands-on experience vs. theoretical knowledge
        
        AI Score (0-100) should assess:
        - Machine Learning concepts (regression, classification, clustering)
        - Deep Learning experience (CNNs, RNNs, neural networks)
        - NLP concepts (tokenization, sentiment analysis, embeddings)
        - Relevant tools and libraries (TensorFlow, Scikit-learn, Keras)
        - Data processing and analysis skills
        - Model evaluation, testing, and deployment experience
        
        For both scores, consider:
        - Real-world application vs. academic knowledge
        - Recency of skills (modern frameworks vs. outdated)
        - Project complexity and impact
        - Position of keywords (Skills section vs. actual work experience)
        
        Resume Content:
        {resume_content}
        
        Provide results in the following JSON format:
        
        ```json
        {{
          "GenAI": {{
            "score": [0-100 score],
            "explanation": "Concise explanation of score",
            "strengths": ["Strength 1", "Strength 2", ...],
            "improvements": ["Area for improvement 1", "Area for improvement 2", ...]
          }},
          "AI": {{
            "score": [0-100 score],
            "explanation": "Concise explanation of score",
            "strengths": ["Strength 1", "Strength 2", ...],
            "improvements": ["Area for improvement 1", "Area for improvement 2", ...]
          }}
        }}
        ```
        
        Return only the JSON object, no additional text.
        """
        
        try:
            # Make the API call with retry
            response = self._make_api_call_with_retry(prompt)
            
            # Parse the response to extract JSON
            try:
                # Extract just the JSON part if there's surrounding text
                json_text = response
                if "```json" in response:
                    json_text = response.split("```json")[1].split("```")[0]
                elif "```" in response:
                    json_text = response.split("```")[1].split("```")[0]
                
                # Clean up and parse
                json_text = json_text.strip()
                scores = json.loads(json_text)
                
                # Ensure consistent data structure
                for key in ["GenAI", "AI"]:
                    if key not in scores:
                        scores[key] = {}
                    
                    if "score" not in scores[key]:
                        scores[key]["score"] = 50
                    
                    if "explanation" not in scores[key]:
                        scores[key]["explanation"] = "No explanation provided"
                    
                    if "strengths" not in scores[key]:
                        scores[key]["strengths"] = []
                    
                    if "improvements" not in scores[key]:
                        scores[key]["improvements"] = []
                
                return scores
                
            except (json.JSONDecodeError, IndexError):
                # If parsing fails, extract scores using regex
                print("Failed to parse JSON, falling back to text parsing")
                scores = {
                    "GenAI": {
                        "score": self._extract_score(response, "GenAI"),
                        "explanation": self._extract_paragraph(response, "GenAI"),
                        "strengths": self._extract_list_items(response, "strengths", "GenAI"),
                        "improvements": self._extract_list_items(response, "improvements", "GenAI")
                    },
                    "AI": {
                        "score": self._extract_score(response, "AI"),
                        "explanation": self._extract_paragraph(response, "AI"),
                        "strengths": self._extract_list_items(response, "strengths", "AI"),
                        "improvements": self._extract_list_items(response, "improvements", "AI")
                    }
                }
                
                return scores
                
        except Exception as e:
            print(f"Error calculating resume scores: {str(e)}")
            # Return default scores on error
            return {
                "GenAI": {
                    "score": 50,
                    "explanation": "Score could not be calculated due to an error",
                    "strengths": ["Experience with programming", "Technical background"],
                    "improvements": ["Add more GenAI-specific keywords", "Highlight any GenAI projects"]
                },
                "AI": {
                    "score": 50,
                    "explanation": "Score could not be calculated due to an error",
                    "strengths": ["Technical skills", "Programming knowledge"],
                    "improvements": ["Add more AI-specific keywords", "Highlight any AI projects"]
                }
            }
    
    def enhance_resume(self, resume_sections, scores):
        """
        Generate enhancements for a resume based on sections and scores
        
        Args:
            resume_sections: Dictionary with extracted resume sections
            scores: Dictionary with GenAI and AI scores
        
        Returns:
            dict: Dictionary with enhanced sections
        """
        # Convert resume sections to a string for the prompt
        resume_content = "\n\n".join([f"{key}:\n{value}" for key, value in resume_sections.items() if value != "Missing"])
        
        genai_improvements = ", ".join(scores['GenAI']['improvements'])
        ai_improvements = ", ".join(scores['AI']['improvements'])
        
        prompt = f"""
        As an expert resume enhancement AI specializing in GenAI and AI careers, improve the following resume sections.
        
        Current GenAI Score: {scores['GenAI']['score']}/100
        Current AI Score: {scores['AI']['score']}/100
        
        Areas for improvement in GenAI: {genai_improvements}
        Areas for improvement in AI: {ai_improvements}
        
        For EACH section of the resume, provide a carefully enhanced version that:
        1. Improves impact through stronger action verbs and clear, concise phrasing
        2. Naturally integrates relevant GenAI and AI keywords where appropriate
        3. Quantifies achievements with metrics where possible (e.g., "improved model accuracy by 25%")
        4. Follows ATS-friendly formatting and best practices for technical resumes
        5. Maintains the original information while making it more compelling
        
        Resume Sections:
        {resume_content}
        
        Respond with a JSON object containing BOTH the original and enhanced versions of EACH section:
        
        ```json
        {{
          "Section Name 1": {{
            "original": "Original content here",
            "enhanced": "Enhanced content here"
          }},
          "Section Name 2": {{
            "original": "Original content here",
            "enhanced": "Enhanced content here"
          }}
        }}
        ```
        
        Include ALL original sections in your response, with both the original and enhanced content.
        DO NOT invent new information - enhance what is there.
        """
        
        try:
            # Make the API call with retry
            response = self._make_api_call_with_retry(prompt)
            
            # Parse the response to extract JSON
            try:
                # Extract the JSON part if there's surrounding text
                json_text = response
                if "```json" in response:
                    json_text = response.split("```json")[1].split("```")[0]
                elif "```" in response:
                    json_text = response.split("```")[1].split("```")[0]
                
                # Clean up and parse
                json_text = json_text.strip()
                enhanced_sections = json.loads(json_text)
                
                # Validate the format
                validated_sections = {}
                for section, content in enhanced_sections.items():
                    if isinstance(content, dict) and "original" in content and "enhanced" in content:
                        validated_sections[section] = content
                    elif isinstance(content, str):
                        # Handle case where only enhanced content is provided
                        original = resume_sections.get(section, "Missing")
                        validated_sections[section] = {
                            "original": original,
                            "enhanced": content
                        }
                
                # Add any sections that were in the original but not in the response
                for section, content in resume_sections.items():
                    if section not in validated_sections and content != "Missing":
                        validated_sections[section] = {
                            "original": content,
                            "enhanced": content  # Default to unchanged
                        }
                
                return validated_sections
                
            except (json.JSONDecodeError, IndexError):
                # If parsing fails, construct manually
                print("Failed to parse JSON, constructing manually")
                enhanced_sections = {}
                
                # Get all section names from the original
                for section, content in resume_sections.items():
                    if content != "Missing":
                        enhanced_sections[section] = {
                            "original": content,
                            "enhanced": content  # Default to unchanged
                        }
                
                # Look for enhanced sections in the text response
                for section in enhanced_sections.keys():
                    # Look for section header followed by content
                    pattern = f"{section}[:\\s]+([\\s\\S]+?)(?=\\n\\n|$)"
                    import re
                    matches = re.search(pattern, response)
                    if matches:
                        enhanced_sections[section]["enhanced"] = matches.group(1).strip()
                
                return enhanced_sections
                
        except Exception as e:
            print(f"Error enhancing resume: {str(e)}")
            # Return original sections on error
            enhanced_sections = {}
            for section, content in resume_sections.items():
                if content != "Missing":
                    enhanced_sections[section] = {
                        "original": content,
                        "enhanced": content  # Default to unchanged
                    }
            return enhanced_sections
    
    def match_resume_to_job(self, resume_sections, job_description):
        """
        Match resume content against a job description
        
        Args:
            resume_sections: Dictionary with extracted resume sections
            job_description: Job description text
        
        Returns:
            dict: Dictionary with match results and suggestions
        """
        # Convert resume sections to a string
        resume_content = "\n\n".join([f"{key}:\n{value}" for key, value in resume_sections.items() if value != "Missing"])
        
        prompt = f"""
        As an advanced resume-job matching AI, perform a comprehensive analysis of how well this resume matches the job description.
        
        Resume Content:
        {resume_content}
        
        Job Description:
        {job_description}
        
        Provide a detailed matching analysis with the following components:
        
        1. An overall match score (0-100)
        2. A breakdown of the match score by dimension:
           - Skills match (0-100)
           - Experience match (0-100)
           - Education match (0-100)
           - Technical keyword match (0-100)
        3. List of key matching strengths (what aligns well)
        4. List of gaps and misalignments (what's missing or needs improvement)
        5. Key job requirements extracted from the description
        
        Format your response as a JSON object with the following structure:
        
        ```json
        {{
          "match_score": 75,
          "score_breakdown": {{
            "skills_match": 80,
            "experience_match": 70,
            "education_match": 85,
            "keyword_match": 65
          }},
          "matching_strengths": [
            "Strong technical skills in required technologies",
            "Relevant experience in similar roles",
            "Educational background aligns with requirements"
          ],
          "gaps_and_misalignments": [
            "Missing experience with specific tool mentioned in job",
            "Could emphasize leadership more to match requirements",
            "Certifications mentioned in job not present in resume"
          ],
          "key_requirements": [
            "5+ years experience in software development",
            "Proficiency in Python and JavaScript",
            "Bachelor's degree in Computer Science or related field",
            "Experience with cloud technologies (AWS/Azure)"
          ]
        }}
        ```
        
        Return only the JSON object, no additional text.
        """
        
        try:
            # Make the API call with retry
            response = self._make_api_call_with_retry(prompt)
            
            # Parse the response to extract JSON
            try:
                # Extract the JSON part if there's surrounding text
                json_text = response
                if "```json" in response:
                    json_text = response.split("```json")[1].split("```")[0]
                elif "```" in response:
                    json_text = response.split("```")[1].split("```")[0]
                
                # Clean up and parse
                json_text = json_text.strip()
                match_result = json.loads(json_text)
                
                # Ensure all expected fields are present
                if "match_score" not in match_result:
                    match_result["match_score"] = 50
                
                if "score_breakdown" not in match_result:
                    match_result["score_breakdown"] = {
                        "skills_match": 50,
                        "experience_match": 50,
                        "education_match": 50,
                        "keyword_match": 50
                    }
                
                if "matching_strengths" not in match_result:
                    match_result["matching_strengths"] = []
                
                if "gaps_and_misalignments" not in match_result:
                    match_result["gaps_and_misalignments"] = []
                
                if "key_requirements" not in match_result:
                    match_result["key_requirements"] = []
                
                return match_result
                
            except (json.JSONDecodeError, IndexError):
                # If parsing fails, extract data using regex or text parsing
                print("Failed to parse JSON, constructing manually")
                import re
                
                match_score = self._extract_score(response, "match score")
                
                # Extract score breakdown
                skills_match = self._extract_score(response, "skills match")
                experience_match = self._extract_score(response, "experience match")
                education_match = self._extract_score(response, "education match")
                keyword_match = self._extract_score(response, "keyword match")
                
                # Extract lists
                strengths = self._extract_list_items(response, "strengths|matching strengths")
                gaps = self._extract_list_items(response, "gaps|misalignments")
                requirements = self._extract_list_items(response, "requirements|key requirements")
                
                match_result = {
                    "match_score": match_score,
                    "score_breakdown": {
                        "skills_match": skills_match,
                        "experience_match": experience_match,
                        "education_match": education_match,
                        "keyword_match": keyword_match
                    },
                    "matching_strengths": strengths,
                    "gaps_and_misalignments": gaps,
                    "key_requirements": requirements
                }
                
                return match_result
                
        except Exception as e:
            print(f"Error matching resume to job: {str(e)}")
            # Return default result on error
            return {
                "match_score": 50,
                "score_breakdown": {
                    "skills_match": 50,
                    "experience_match": 50,
                    "education_match": 50,
                    "keyword_match": 50
                },
                "matching_strengths": ["Technical background", "Education"],
                "gaps_and_misalignments": ["Could not fully analyze gaps due to an error"],
                "key_requirements": ["Could not extract key requirements due to an error"]
            }
    
    def enhance_resume_for_job(self, resume_sections, job_description, match_result):
        """
        Generate job-tailored resume enhancements
        
        Args:
            resume_sections: Dictionary with extracted resume sections
            job_description: Job description text
            match_result: Result from match_resume_to_job
        
        Returns:
            dict: Dictionary with job-tailored sections
        """
        # Convert resume sections to a string
        resume_content = "\n\n".join([f"{key}:\n{value}" for key, value in resume_sections.items() if value != "Missing"])
        
        # Extract gaps for the prompt
        gaps = "\n".join([f"- {gap}" for gap in match_result.get("gaps_and_misalignments", [])])
        requirements = "\n".join([f"- {req}" for req in match_result.get("key_requirements", [])])
        
        prompt = f"""
        As an expert resume tailoring AI, enhance this resume specifically for this job description. The current match score is {match_result.get('match_score', 50)}/100.
        
        Resume Content:
        {resume_content}
        
        Job Description:
        {job_description}
        
        Current Gaps and Misalignments:
        {gaps}
        
        Key Job Requirements:
        {requirements}
        
        For EACH section of the resume, provide a tailored version that:
        1. Aligns content with the specific job requirements
        2. Emphasizes relevant skills and experiences that match the job
        3. Uses keywords from the job description naturally
        4. Addresses identified gaps where possible
        5. Quantifies achievements that would be valued in this role
        6. Maintains honesty and accuracy - don't fabricate experience
        
        Respond with a JSON object containing BOTH the original and enhanced versions of EACH section:
        
        ```json
        {{
          "Section Name 1": {{
            "original": "Original content here",
            "enhanced": "Job-tailored content here"
          }},
          "Section Name 2": {{
            "original": "Original content here",
            "enhanced": "Job-tailored content here"
          }}
        }}
        ```
        
        Include ALL original sections in your response, with both the original and tailored content.
        """
        
        try:
            # Make the API call with retry
            response = self._make_api_call_with_retry(prompt)
            
            # Parse the response to extract JSON
            try:
                # Extract the JSON part if there's surrounding text
                json_text = response
                if "```json" in response:
                    json_text = response.split("```json")[1].split("```")[0]
                elif "```" in response:
                    json_text = response.split("```")[1].split("```")[0]
                
                # Clean up and parse
                json_text = json_text.strip()
                tailored_sections = json.loads(json_text)
                
                # Validate the format
                validated_sections = {}
                for section, content in tailored_sections.items():
                    if isinstance(content, dict) and "original" in content and "enhanced" in content:
                        validated_sections[section] = content
                    elif isinstance(content, str):
                        # Handle case where only enhanced content is provided
                        original = resume_sections.get(section, "Missing")
                        validated_sections[section] = {
                            "original": original,
                            "enhanced": content
                        }
                
                # Add any sections that were in the original but not in the response
                for section, content in resume_sections.items():
                    if section not in validated_sections and content != "Missing":
                        validated_sections[section] = {
                            "original": content,
                            "enhanced": content  # Default to unchanged
                        }
                
                return validated_sections
                
            except (json.JSONDecodeError, IndexError):
                # If parsing fails, construct manually
                print("Failed to parse JSON, constructing manually")
                tailored_sections = {}
                
                # Get all section names from the original
                for section, content in resume_sections.items():
                    if content != "Missing":
                        tailored_sections[section] = {
                            "original": content,
                            "enhanced": content  # Default to unchanged
                        }
                
                # Look for enhanced sections in the text response
                for section in tailored_sections.keys():
                    # Look for section header followed by content
                    pattern = f"{section}[:\\s]+([\\s\\S]+?)(?=\\n\\n|$)"
                    import re
                    matches = re.search(pattern, response)
                    if matches:
                        tailored_sections[section]["enhanced"] = matches.group(1).strip()
                
                return tailored_sections
                
        except Exception as e:
            print(f"Error tailoring resume for job: {str(e)}")
            # Return original sections on error
            tailored_sections = {}
            for section, content in resume_sections.items():
                if content != "Missing":
                    tailored_sections[section] = {
                        "original": content,
                        "enhanced": content  # Default to unchanged
                    }
            return tailored_sections
    
    def _make_api_call_with_retry(self, prompt, max_retries=3, base_wait_time=2):
        """
        Make an API call with exponential backoff retry
        
        Args:
            prompt: The prompt text for the API call
            max_retries: Maximum number of retry attempts
            base_wait_time: Base time to wait between retries (doubles each retry)
        
        Returns:
            str: The response text
        """
        attempt = 0
        last_exception = None
        
        while attempt < max_retries:
            try:
                response = self.model.generate_content(prompt)
                return response.text
            except Exception as e:
                last_exception = e
                attempt += 1
                wait_time = base_wait_time * (2 ** (attempt - 1))
                print(f"API call failed. Retrying in {wait_time} seconds. ({attempt}/{max_retries})")
                time.sleep(wait_time)
        
        # If we got here, all retries failed
        print(f"All retries failed: {last_exception}")
        raise last_exception
    
    def _extract_score(self, text, score_type, default=50):
        """
        Extract a numeric score from text
        
        Args:
            text: The text to search in
            score_type: Type of score to look for (e.g., "GenAI", "match score")
            default: Default score if extraction fails
        
        Returns:
            int: The extracted score
        """
        import re
        
        # Look for patterns like "GenAI Score: 75" or "Match Score: 65/100"
        patterns = [
            rf"{score_type}:?\s*(\d+)(?:/100)?",
            rf"{score_type}.*?(\d+)(?:/100)?",
        ]
        
        for pattern in patterns:
            matches = re.search(pattern, text, re.IGNORECASE)
            if matches:
                try:
                    return int(matches.group(1))
                except (ValueError, IndexError):
                    continue
        
        return default
    
    def _extract_paragraph(self, text, section, default="No explanation provided"):
        """
        Extract a paragraph of text related to a section
        
        Args:
            text: The text to search in
            section: Section to look for (e.g., "GenAI", "AI")
            default: Default text if extraction fails
        
        Returns:
            str: The extracted paragraph
        """
        import re
        
        # Look for a paragraph after section header
        pattern = rf"{section}.*?explanation:?\s*(.*?)(?=\n\n|\n[A-Z]|\Z)"
        matches = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        
        if matches:
            return matches.group(1).strip()
        
        return default
    
    def _extract_list_items(self, text, list_type, section=None):
        """
        Extract list items from text
        
        Args:
            text: The text to search in
            list_type: Type of list to look for (e.g., "strengths", "improvements")
            section: Optional section to search within (e.g., "GenAI", "AI")
        
        Returns:
            list: Extracted list items
        """
        import re
        
        # If section is specified, narrow down the text
        if section:
            section_pattern = rf"{section}.*?(?=\n\n[A-Z]|\Z)"
            section_matches = re.search(section_pattern, text, re.IGNORECASE | re.DOTALL)
            if section_matches:
                text = section_matches.group(0)
        
        # Look for a list after the list type
        list_pattern = rf"{list_type}:?\s*((?:\n?[-*•].*)+)"
        list_matches = re.search(list_pattern, text, re.IGNORECASE | re.DOTALL)
        
        if list_matches:
            list_text = list_matches.group(1)
            # Extract individual items
            items = re.findall(r"[-*•]\s*(.*?)(?=\n[-*•]|\Z)", list_text, re.DOTALL)
            return [item.strip() for item in items]
        
        return []

class GeminiClient:
    def __init__(self):
        self.gemini_api_key = API_CONFIG["google_cloud"]["gemini_api_key"]
        self.initialized = False
        self.model = None
        self.initialize_gemini()
        
    def initialize_gemini(self):
        """Initialize Gemini API client with API key"""
        if self.initialized:
            return
            
        if not self.gemini_api_key:
            st.warning("Gemini API key not configured. Using simulated responses.")
            return
            
        try:
            # Configure the Gemini API
            genai.configure(api_key=self.gemini_api_key)
            
            # Get the default text model
            self.model = genai.GenerativeModel('gemini-pro')
            self.initialized = True
            
        except Exception as e:
            st.warning(f"Gemini API initialization error: {str(e)}. Using simulated responses.")
    
    def generate_text(self, prompt, temperature=0.7, max_output_tokens=1024, use_mock=False):
        """
        Generate text using Gemini API
        
        Args:
            prompt: The text prompt for generation
            temperature: Controls randomness (0.0-1.0)
            max_output_tokens: Maximum length of generated text
            use_mock: Whether to use mock responses
            
        Returns:
            str: Generated text
        """
        if not self.initialized or use_mock:
            return self._get_mock_response(prompt)
            
        try:
            # Generate content
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=temperature,
                    max_output_tokens=max_output_tokens,
                    top_p=0.95,
                    top_k=40,
                )
            )
            
            return response.text
            
        except Exception as e:
            st.warning(f"Gemini API error: {str(e)}. Using simulated response.")
            return self._get_mock_response(prompt)
    
    def _get_mock_response(self, prompt):
        """
        Generate a mock response when the API is unavailable
        
        Args:
            prompt: The original prompt
            
        Returns:
            str: Mock response text
        """
        # Generate different mock responses based on prompt content
        
        if "extract sections" in prompt.lower() or "parse resume" in prompt.lower():
            # Mock response for resume section extraction
            return json.dumps({
                "Contact": "John Doe, john.doe@example.com, (555) 123-4567, LinkedIn: linkedin.com/in/johndoe",
                "Summary": "Experienced software engineer with 5 years of experience in AI and machine learning.",
                "Education": "Master of Science in Computer Science, Stanford University, 2018-2020",
                "Work Experience": "AI Engineer, TechCorp Inc., 2020-Present\n- Developed machine learning models\n- Implemented NLP solutions\n- Collaborated with cross-functional teams",
                "Skills": "Python, TensorFlow, PyTorch, NLP, Deep Learning, SQL, Cloud Computing",
                "Projects": "Sentiment Analysis Tool: Built an NLP-based sentiment analyzer with 93% accuracy",
                "Certifications": "Google Cloud Professional Data Engineer, AWS Certified Machine Learning Specialist",
                "Languages": "English (Native), Spanish (Intermediate)"
            })
        
        elif "score resume" in prompt.lower() or "evaluate resume" in prompt.lower():
            # Mock response for resume scoring
            return json.dumps({
                "GenAI": {
                    "score": 75,
                    "explanation": "The resume demonstrates good knowledge of AI technologies but lacks specific GenAI projects.",
                    "strengths": [
                        "Good foundation in machine learning",
                        "Experience with Python and relevant libraries",
                        "Understanding of NLP concepts"
                    ],
                    "improvements": [
                        "Add specific GenAI projects or experiences",
                        "Highlight any work with large language models",
                        "Include experience with specific GenAI frameworks"
                    ]
                },
                "AI": {
                    "score": 82,
                    "explanation": "Strong AI background with practical implementation experience.",
                    "strengths": [
                        "Solid experience with machine learning projects",
                        "Practical application of NLP techniques",
                        "Understanding of deep learning frameworks"
                    ],
                    "improvements": [
                        "Add more quantifiable results from AI projects",
                        "Include performance metrics of implemented models",
                        "Highlight experience with real-world data challenges"
                    ]
                }
            })
        
        elif "match resume" in prompt.lower() or "job description" in prompt.lower():
            # Mock response for resume-job matching
            return json.dumps({
                "match_score": 68,
                "match_breakdown": {
                    "skills_match": 72,
                    "experience_match": 65,
                    "education_match": 90,
                    "overall_relevance": 68
                },
                "matching_strengths": [
                    "Strong educational background in required field",
                    "Experience with several required technologies",
                    "Demonstrated project work in relevant domains"
                ],
                "gaps_and_misalignments": [
                    "Limited experience with cloud deployment",
                    "No mention of agile development methodologies",
                    "Missing experience with required technology: Docker"
                ],
                "job_requirements": {
                    "required_skills": ["Python", "TensorFlow", "Docker", "AWS", "Agile"],
                    "preferred_qualifications": ["PhD in Computer Science", "5+ years experience", "Published research"],
                    "responsibilities": ["Develop ML models", "Deploy solutions to production", "Collaborate with product teams"]
                }
            })
        
        elif "enhance resume" in prompt.lower() or "improve resume" in prompt.lower():
            # Mock response for resume enhancement
            return json.dumps({
                "Summary": {
                    "original": "Experienced software engineer with 5 years of experience in AI and machine learning.",
                    "enhanced": "Results-driven AI Engineer with 5+ years of expertise developing and deploying production-ready machine learning solutions that drive business value. Specialized in NLP applications and deep learning architectures."
                },
                "Work Experience": {
                    "original": "AI Engineer, TechCorp Inc., 2020-Present\n- Developed machine learning models\n- Implemented NLP solutions\n- Collaborated with cross-functional teams",
                    "enhanced": "AI Engineer, TechCorp Inc., 2020-Present\n- Architected and deployed machine learning models that increased customer engagement by 35%\n- Developed NLP solution that automated document processing, saving 20+ hours weekly\n- Led cross-functional team of 5 engineers to deliver ML pipeline with 99.9% uptime"
                },
                "Skills": {
                    "original": "Python, TensorFlow, PyTorch, NLP, Deep Learning, SQL, Cloud Computing",
                    "enhanced": "Python, TensorFlow, PyTorch, Transformers, BERT, GPT, RAG, Vector Databases, NLP, Deep Learning, MLOps, Docker, Kubernetes, AWS, SQL, NoSQL, CI/CD"
                }
            })
        
        else:
            # Generic response
            return "This is a simulated response from the Gemini API. In a real implementation, this would be generated by the AI model."
    
    def extract_resume_sections(self, resume_text):
        """
        Extract structured sections from a resume
        
        Args:
            resume_text: Full text of the resume
            
        Returns:
            dict: Extracted sections with their content
        """
        prompt = f"""
        Extract and organize the key sections from the following resume text.
        
        Return the result as a JSON object with the following sections (if present):
        - Contact: Contact information including name, email, phone, address, LinkedIn, etc.
        - Summary: Professional summary or objective statement
        - Education: Educational background and qualifications
        - Work Experience: Professional experience and achievements
        - Skills: Technical and professional skills
        - Projects: Notable projects and their descriptions
        - Certifications: Professional certifications
        - Languages: Language proficiencies
        - Awards: Awards and recognitions
        - Publications: Academic or professional publications
        - Volunteering: Volunteer experiences
        
        If a section is not present in the resume, include the key but mark the value as "Missing".
        
        Resume Text:
        {resume_text}
        
        Return only the JSON object with no additional text.
        """
        
        try:
            response_text = self.generate_text(prompt)
            
            # Extract JSON object from response if needed
            json_match = re.search(r'({[\s\S]*})', response_text)
            json_str = json_match.group(1) if json_match else response_text
            
            # Parse the JSON
            sections = json.loads(json_str)
            return sections
            
        except Exception as e:
            st.error(f"Error extracting resume sections: {str(e)}")
            # Return a basic structure if extraction fails
            return {
                "Contact": resume_text[:100] + "..." if len(resume_text) > 100 else resume_text,
                "Summary": "Missing",
                "Education": "Missing",
                "Work Experience": "Missing",
                "Skills": "Missing",
                "Projects": "Missing",
                "Certifications": "Missing",
                "Languages": "Missing"
            }
    
    def calculate_resume_scores(self, resume_sections):
        """
        Calculate AI and GenAI relevance scores for a resume
        
        Args:
            resume_sections: Dictionary of resume sections
            
        Returns:
            dict: Scores and explanations for different categories
        """
        # Combine resume sections into a single text for scoring
        resume_text = ""
        for section, content in resume_sections.items():
            if content != "Missing":
                resume_text += f"{section}:\n{content}\n\n"
        
        prompt = f"""
        Analyze the following resume and score it for relevance to two categories:
        1. GenAI (Generative AI): Score relevance to generative AI fields, including large language models,
           text generation, image generation, diffusion models, transformers, etc.
        2. AI (General Artificial Intelligence): Score relevance to general AI fields, including machine learning,
           deep learning, neural networks, computer vision, NLP, etc.
        
        For each category, provide:
        - A score from 0-100
        - A brief explanation for the score
        - 3 strengths related to the category
        - 3 areas for improvement
        
        Resume:
        {resume_text}
        
        Return the results as a JSON object with the following structure:
        {{
            "GenAI": {{
                "score": <score>,
                "explanation": <explanation>,
                "strengths": [<strength1>, <strength2>, <strength3>],
                "improvements": [<improvement1>, <improvement2>, <improvement3>]
            }},
            "AI": {{
                "score": <score>,
                "explanation": <explanation>,
                "strengths": [<strength1>, <strength2>, <strength3>],
                "improvements": [<improvement1>, <improvement2>, <improvement3>]
            }}
        }}
        
        Return only the JSON object with no additional text.
        """
        
        try:
            response_text = self.generate_text(prompt)
            
            # Extract JSON object from response if needed
            json_match = re.search(r'({[\s\S]*})', response_text)
            json_str = json_match.group(1) if json_match else response_text
            
            # Parse the JSON
            scores = json.loads(json_str)
            return scores
            
        except Exception as e:
            st.error(f"Error calculating resume scores: {str(e)}")
            # Return a default scoring if calculation fails
            return {
                "GenAI": {
                    "score": 50,
                    "explanation": "Score calculation failed, showing default values",
                    "strengths": ["Unable to determine strengths"],
                    "improvements": ["Try again with more complete resume sections"]
                },
                "AI": {
                    "score": 60,
                    "explanation": "Score calculation failed, showing default values",
                    "strengths": ["Unable to determine strengths"],
                    "improvements": ["Try again with more complete resume sections"]
                }
            }
    
    def match_resume_to_job(self, resume_sections, job_description):
        """
        Match a resume against a job description
        
        Args:
            resume_sections: Dictionary of resume sections
            job_description: Job description text
            
        Returns:
            dict: Matching results including score and recommendations
        """
        # Combine resume sections into a single text for matching
        resume_text = ""
        for section, content in resume_sections.items():
            if content != "Missing":
                resume_text += f"{section}:\n{content}\n\n"
        
        prompt = f"""
        Analyze how well the following resume matches the provided job description.
        
        Resume:
        {resume_text}
        
        Job Description:
        {job_description}
        
        Provide a comprehensive match analysis with the following:
        1. An overall match score from 0-100
        2. A breakdown of matching scores for different aspects (skills, experience, education, overall relevance)
        3. Key matching strengths (where the resume aligns well with the job)
        4. Gaps and misalignments (where the resume doesn't meet job requirements)
        5. Key job requirements extracted from the job description
        
        Return the results as a JSON object with the following structure:
        {{
            "match_score": <overall_score>,
            "match_breakdown": {{
                "skills_match": <score>,
                "experience_match": <score>,
                "education_match": <score>,
                "overall_relevance": <score>
            }},
            "matching_strengths": [<strength1>, <strength2>, ...],
            "gaps_and_misalignments": [<gap1>, <gap2>, ...],
            "job_requirements": {{
                "required_skills": [<skill1>, <skill2>, ...],
                "preferred_qualifications": [<qual1>, <qual2>, ...],
                "responsibilities": [<resp1>, <resp2>, ...]
            }}
        }}
        
        Return only the JSON object with no additional text.
        """
        
        try:
            response_text = self.generate_text(prompt)
            
            # Extract JSON object from response if needed
            json_match = re.search(r'({[\s\S]*})', response_text)
            json_str = json_match.group(1) if json_match else response_text
            
            # Parse the JSON
            match_result = json.loads(json_str)
            return match_result
            
        except Exception as e:
            st.error(f"Error matching resume to job: {str(e)}")
            # Return a default matching result if matching fails
            return {
                "match_score": 50,
                "match_breakdown": {
                    "skills_match": 50,
                    "experience_match": 50,
                    "education_match": 50,
                    "overall_relevance": 50
                },
                "matching_strengths": ["Unable to determine matching strengths"],
                "gaps_and_misalignments": ["Unable to determine gaps"],
                "job_requirements": {
                    "required_skills": ["Unable to extract required skills"],
                    "preferred_qualifications": ["Unable to extract qualifications"],
                    "responsibilities": ["Unable to extract responsibilities"]
                }
            }
    
    def enhance_resume(self, resume_sections, scores, region="north_america"):
        """
        Generate enhanced content for resume sections
        
        Args:
            resume_sections: Dictionary of resume sections
            scores: Scoring results from calculate_resume_scores
            region: Target region for resume standards
            
        Returns:
            dict: Enhanced resume sections with original and improved content
        """
        # Create input context from scores and region
        context = {
            "scores": scores,
            "region": region
        }
        
        prompt = f"""
        Enhance the following resume sections to improve their effectiveness and impact.
        Use the provided scores and regional preferences to guide your enhancements.
        
        Current Score Information:
        GenAI Score: {scores['GenAI']['score']}
        AI Score: {scores['AI']['score']}
        
        Improvement Areas for GenAI:
        {', '.join(scores['GenAI']['improvements'])}
        
        Improvement Areas for AI:
        {', '.join(scores['AI']['improvements'])}
        
        Target Region: {region}
        
        For each section, provide the original content and an enhanced version that:
        1. Improves clarity and impact
        2. Emphasizes relevant skills and experiences
        3. Uses more powerful and specific language
        4. Addresses the improvement areas identified in the scores
        5. Follows the resume standards for the target region
        
        Resume Sections:
        {json.dumps(resume_sections, indent=2)}
        
        Return the results as a JSON object with the following structure for each section:
        {{
            "section_name": {{
                "original": <original_content>,
                "enhanced": <enhanced_content>
            }},
            ...
        }}
        
        Return only the JSON object with no additional text.
        """
        
        try:
            response_text = self.generate_text(prompt)
            
            # Extract JSON object from response if needed
            json_match = re.search(r'({[\s\S]*})', response_text)
            json_str = json_match.group(1) if json_match else response_text
            
            # Parse the JSON
            enhanced_sections = json.loads(json_str)
            return enhanced_sections
            
        except Exception as e:
            st.error(f"Error enhancing resume: {str(e)}")
            
            # Return a basic enhancement if fails
            enhanced_sections = {}
            for section, content in resume_sections.items():
                if content == "Missing":
                    enhanced_sections[section] = {
                        "original": "Missing",
                        "enhanced": "Missing"
                    }
                else:
                    enhanced_sections[section] = {
                        "original": content,
                        "enhanced": content + " [Enhancement failed]"
                    }
            
            return enhanced_sections
    
    def enhance_resume_for_job(self, resume_sections, job_description, match_result):
        """
        Tailor resume sections for a specific job
        
        Args:
            resume_sections: Dictionary of resume sections
            job_description: Job description text
            match_result: Results from match_resume_to_job
            
        Returns:
            dict: Enhanced resume sections tailored for the job
        """
        prompt = f"""
        Tailor the following resume sections specifically for the provided job description.
        Use the match analysis to address gaps and highlight relevant strengths.
        
        Job Description:
        {job_description}
        
        Match Score: {match_result.get('match_score', 'N/A')}
        
        Matching Strengths:
        {', '.join(match_result.get('matching_strengths', ['N/A']))}
        
        Gaps and Misalignments:
        {', '.join(match_result.get('gaps_and_misalignments', ['N/A']))}
        
        For each resume section, provide an enhanced version that:
        1. Aligns terminology with the job description
        2. Highlights experiences and skills most relevant to this job
        3. Addresses identified gaps where possible
        4. Uses keywords from the job description appropriately
        5. Maintains truthfulness while presenting information in the most relevant way
        
        Resume Sections:
        {json.dumps(resume_sections, indent=2)}
        
        Return the results as a JSON object with the following structure for each section:
        {{
            "section_name": {{
                "original": <original_content>,
                "tailored": <tailored_content>,
                "explanation": <brief explanation of changes>
            }},
            ...
        }}
        
        Return only the JSON object with no additional text.
        """
        
        try:
            response_text = self.generate_text(prompt)
            
            # Extract JSON object from response if needed
            json_match = re.search(r'({[\s\S]*})', response_text)
            json_str = json_match.group(1) if json_match else response_text
            
            # Parse the JSON
            tailored_sections = json.loads(json_str)
            return tailored_sections
            
        except Exception as e:
            st.error(f"Error tailoring resume for job: {str(e)}")
            
            # Return a basic tailoring if fails
            tailored_sections = {}
            for section, content in resume_sections.items():
                if content == "Missing":
                    tailored_sections[section] = {
                        "original": "Missing",
                        "tailored": "Missing",
                        "explanation": "N/A"
                    }
                else:
                    tailored_sections[section] = {
                        "original": content,
                        "tailored": content + " [Job-specific tailoring failed]",
                        "explanation": "Unable to generate tailored content due to an error"
                    }
            
            return tailored_sections

# Initialize Gemini client
gemini_client = GeminiClient() 