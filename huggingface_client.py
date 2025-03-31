import requests
import json
import streamlit as st
import numpy as np
import time
from utils.api_config import API_CONFIG

class HuggingFaceClient:
    def __init__(self):
        self.hf_config = API_CONFIG["huggingface"]
        self.api_key = self.hf_config["api_key"]
        self.resume_scoring_model = self.hf_config["resume_scoring_model"]
        self.resume_matching_model = self.hf_config["resume_matching_model"]
        self.base_url = "https://api-inference.huggingface.co/models/"
        
    def _call_model(self, model_name, payload, use_mock=True):
        """
        Make an inference request to a Hugging Face model
        
        Args:
            model_name: Name of the Hugging Face model
            payload: JSON-serializable request payload
            use_mock: Whether to use mock responses when API is unavailable
            
        Returns:
            dict: Model response
        """
        # If API key is not configured, use mock responses
        if not self.api_key or use_mock:
            return self._get_mock_response(model_name, payload)
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(
                f"{self.base_url}{model_name}",
                headers=headers,
                json=payload
            )
            
            if response.status_code == 200:
                return response.json()
            
            # Model may be loading - retry
            if response.status_code == 503:
                st.warning("Model is loading. Please wait...")
                time.sleep(2)
                return self._call_model(model_name, payload)
                
            # Fallback to mock responses
            st.warning(f"API error (status {response.status_code}): {response.text}")
            return self._get_mock_response(model_name, payload)
            
        except Exception as e:
            st.warning(f"API call error: {str(e)}")
            return self._get_mock_response(model_name, payload)
    
    def _get_mock_response(self, model_name, payload):
        """
        Generate a mock response when the API is unavailable
        
        Args:
            model_name: Name of the Hugging Face model
            payload: Original request payload
            
        Returns:
            dict: Mock response in the same format as the API would return
        """
        # Generate different mock responses based on model and input
        if "resume-scoring" in model_name:
            # Mock scoring response
            resume_content = ""
            if "resume_text" in payload:
                resume_content = payload["resume_text"]
            elif "resume_sections" in payload:
                resume_content = " ".join([v for k, v in payload["resume_sections"].items() if v != "Missing"])
            
            # Generate a score based on length and keyword presence
            length_score = min(len(resume_content) / 1000, 1) * 40  # 0-40 based on length
            
            # Check for relevant keywords
            keywords = ["AI", "machine learning", "deep learning", "Python", "TensorFlow", 
                       "PyTorch", "data science", "NLP", "computer vision"]
            
            keyword_score = 0
            for keyword in keywords:
                if keyword.lower() in resume_content.lower():
                    keyword_score += 6  # 6 points per keyword
            
            keyword_score = min(keyword_score, 60)  # Max 60 from keywords
            total_score = int(length_score + keyword_score)
            
            return {
                "score": total_score,
                "explanation": f"Score based on content length ({int(length_score)}) and relevant keywords ({int(keyword_score)})",
                "strengths": [
                    "Clear presentation of technical skills",
                    "Good demonstration of project experience",
                    "Relevant educational background"
                ],
                "improvements": [
                    "Add more quantifiable achievements",
                    "Highlight experience with latest AI technologies",
                    "Add more specific details about projects"
                ]
            }
            
        elif "resume-matching" in model_name:
            # Mock matching response
            resume_content = ""
            job_description = ""
            
            if "resume_sections" in payload:
                resume_content = " ".join([v for k, v in payload["resume_sections"].items() if v != "Missing"])
            
            if "job_description" in payload:
                job_description = payload["job_description"]
            
            # Generate a match score based on simulated relevance
            match_score = np.random.randint(40, 85)  # Random score between 40-85
            
            # More detailed response for demonstration
            return {
                "match_score": match_score,
                "match_details": {
                    "skills_match": np.random.randint(30, 95),
                    "experience_match": np.random.randint(30, 95),
                    "education_match": np.random.randint(30, 95),
                    "overall_relevance": np.random.randint(30, 95)
                },
                "matching_keywords": [
                    "Python", "machine learning", "data analysis",
                    "team collaboration", "project management"
                ],
                "missing_keywords": [
                    "Docker", "Kubernetes", "CI/CD",
                    "cloud infrastructure", "microservices"
                ],
                "improvement_suggestions": [
                    "Highlight your experience with cloud platforms",
                    "Add specific DevOps skills to your resume",
                    "Emphasize your experience with containerization"
                ]
            }
        else:
            # Generic response
            return {"message": "Mock response - API not called"}
    
    def score_resume(self, resume_sections=None, resume_text=None):
        """
        Score a resume for overall quality and relevance
        
        Args:
            resume_sections: Dictionary of resume sections
            resume_text: Full resume text as alternative to sections
            
        Returns:
            dict: Scoring results including score and feedback
        """
        # Prepare the payload - either resume_sections or resume_text
        payload = {}
        if resume_sections:
            payload["resume_sections"] = resume_sections
        elif resume_text:
            payload["resume_text"] = resume_text
        else:
            return {"error": "No resume content provided"}
        
        # Call the model
        result = self._call_model(self.resume_scoring_model, payload)
        
        # Process and return the results
        return {
            "genai_score": result.get("score", 0),
            "explanation": result.get("explanation", ""),
            "strengths": result.get("strengths", []),
            "improvements": result.get("improvements", [])
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
        # Prepare the payload
        payload = {
            "resume_sections": resume_sections,
            "job_description": job_description
        }
        
        # Call the model
        result = self._call_model(self.resume_matching_model, payload)
        
        # Process and return the results
        return {
            "match_score": result.get("match_score", 0),
            "match_details": result.get("match_details", {}),
            "matching_keywords": result.get("matching_keywords", []),
            "missing_keywords": result.get("missing_keywords", []),
            "improvement_suggestions": result.get("improvement_suggestions", [])
        }
    
    def enhance_resume_for_job(self, resume_sections, job_description):
        """
        Generate enhanced resume content tailored for a specific job
        
        Args:
            resume_sections: Dictionary of resume sections
            job_description: Job description text
            
        Returns:
            dict: Enhanced resume sections
        """
        # First, match the resume to the job to get insights
        match_results = self.match_resume_to_job(resume_sections, job_description)
        
        # Prepare the payload for enhancement
        payload = {
            "resume_sections": resume_sections,
            "job_description": job_description,
            "match_results": match_results,
            "task": "enhance_resume"
        }
        
        # This would call a text generation model in a real implementation
        # For now, we'll use a simulated response
        
        # Generate enhanced sections based on resume and job requirements
        enhanced_sections = {}
        
        for section_name, content in resume_sections.items():
            # Skip missing sections
            if content == "Missing":
                enhanced_sections[section_name] = content
                continue
                
            # Simple enhancement logic (would be more sophisticated in real API)
            enhanced_content = content
            
            # Add keywords from job description if they're missing
            for keyword in match_results.get("missing_keywords", []):
                if keyword.lower() not in content.lower():
                    if section_name == "Skills":
                        enhanced_content += f", {keyword}"
                    elif section_name == "Summary" or section_name == "Objective":
                        enhanced_content += f" Experienced with {keyword}."
            
            enhanced_sections[section_name] = enhanced_content
            
        return enhanced_sections

# Initialize the Hugging Face client
huggingface_client = HuggingFaceClient() 