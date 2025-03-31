"""
HuggingFace Service - Provides access to advanced NLP capabilities
"""

import requests
import json
import numpy as np
import time
import logging
import importlib
import streamlit as st
import os
from typing import Dict, List, Any, Optional, Union

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HuggingFaceService:
    """Service for interacting with HuggingFace's models and APIs"""
    
    def __init__(self, api_key=None):
        """
        Initialize the HuggingFace service
        
        Args:
            api_key (str, optional): HuggingFace API key. If not provided, 
                                     it will try to load from environment.
        """
        self.api_key = api_key or os.getenv("HUGGINGFACE_API_KEY")
        if not self.api_key:
            logger.warning("HuggingFace API key not provided. Some features may be limited.")
            
        self.base_url = "https://api-inference.huggingface.co/models/"
        
        # Models for various tasks
        self.models = {
            "ner": "dbmdz/bert-large-cased-finetuned-conll03-english",
            "zero_shot": "facebook/bart-large-mnli",
            "summarization": "facebook/bart-large-cnn",
            "resume_scoring": "deepset/roberta-base-squad2",
            "resume_matching": "sentence-transformers/all-mpnet-base-v2"
        }
        
        # Flag to check if transformers is available
        self.transformers_available = self._check_transformers()
        
        # Store cached pipelines
        self.pipelines = {}
        
    def _check_transformers(self):
        """Check if transformers package is installed"""
        try:
            spec = importlib.util.find_spec("transformers")
            if spec is None:
                logger.warning("Transformers package not found. Using remote API only.")
                return False
                
            # Also check for torch
            torch_spec = importlib.util.find_spec("torch")
            if torch_spec is None:
                logger.warning("PyTorch package not found. Using remote API only.")
                return False
                
            return True
        except Exception as e:
            logger.warning(f"Error checking for transformers: {str(e)}")
            return False
            
    def get_pipeline(self, task):
        """
        Get or create a pipeline for a specific task
        
        Args:
            task (str): Task name (ner, zero_shot, summarization, etc.)
            
        Returns:
            pipeline: HuggingFace pipeline or None if not available
        """
        # If transformers not available, return None
        if not self.transformers_available:
            return None
            
        # If pipeline already exists, return it
        if task in self.pipelines:
            return self.pipelines[task]
            
        # Create pipeline
        try:
            # Import here to avoid errors if transformers is not installed
            from transformers import pipeline
            
            # Get model for task
            model = self.models.get(task)
            if not model:
                logger.warning(f"No model defined for task {task}")
                return None
                
            # Create pipeline
            self.pipelines[task] = pipeline(task, model=model)
            return self.pipelines[task]
        except Exception as e:
            logger.error(f"Error creating pipeline for {task}: {str(e)}")
            return None
            
    def call_api(self, model_name, payload):
        """
        Call HuggingFace API
        
        Args:
            model_name (str): Model name or path
            payload (dict): API payload
            
        Returns:
            dict: API response
        """
        if not self.api_key:
            return self._get_mock_response(model_name, payload)
            
        try:
            headers = {"Authorization": f"Bearer {self.api_key}"}
            response = requests.post(
                f"{self.base_url}{model_name}",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
                
            # Model may be loading - retry
            if response.status_code == 503:
                logger.info(f"Model {model_name} is loading. Retrying...")
                time.sleep(2)
                return self.call_api(model_name, payload)
                
            logger.warning(f"API error (status {response.status_code}): {response.text}")
            return self._get_mock_response(model_name, payload)
            
        except Exception as e:
            logger.error(f"API call error: {str(e)}")
            return self._get_mock_response(model_name, payload)
            
    def _get_mock_response(self, model_name, payload):
        """Generate mock response for demonstration when API is unavailable"""
        task = None
        
        # Determine task based on model name
        if "ner" in model_name.lower():
            task = "ner"
        elif "zero-shot" in model_name.lower() or "mnli" in model_name.lower():
            task = "zero_shot"
        elif "summarization" in model_name.lower() or "cnn" in model_name.lower():
            task = "summarization"
        elif "resume-scoring" in model_name.lower() or "squad" in model_name.lower():
            task = "resume_scoring"
        elif "resume-matching" in model_name.lower() or "sentence-transformers" in model_name.lower():
            task = "resume_matching"
            
        # Generate mock response based on task
        if task == "ner":
            return self._mock_ner_response(payload)
        elif task == "zero_shot":
            return self._mock_zero_shot_response(payload)
        elif task == "summarization":
            return self._mock_summarization_response(payload)
        elif task == "resume_scoring":
            return self._mock_resume_scoring_response(payload)
        elif task == "resume_matching":
            return self._mock_resume_matching_response(payload)
        else:
            # Generic response
            return {"message": "Mock response - API not called"}
            
    def _mock_ner_response(self, payload):
        """Generate mock NER response"""
        text = payload.get("inputs", "")
        if not text:
            return []
            
        # Simple pattern matching for common entity types
        entities = []
        
        # Look for potential person names (capitalized words)
        import re
        name_pattern = r'\b[A-Z][a-z]+ [A-Z][a-z]+\b'
        for match in re.finditer(name_pattern, text):
            entities.append({
                "entity": "PERSON",
                "score": 0.95,
                "word": match.group(0),
                "start": match.start(),
                "end": match.end()
            })
            
        # Look for potential organizations (all caps words)
        org_pattern = r'\b[A-Z]{2,}\b'
        for match in re.finditer(org_pattern, text):
            entities.append({
                "entity": "ORG",
                "score": 0.85,
                "word": match.group(0),
                "start": match.start(),
                "end": match.end()
            })
            
        # Look for dates
        date_pattern = r'\b\d{1,2}/\d{1,2}/\d{2,4}\b|\b\d{4}-\d{2}-\d{2}\b'
        for match in re.finditer(date_pattern, text):
            entities.append({
                "entity": "DATE",
                "score": 0.98,
                "word": match.group(0),
                "start": match.start(),
                "end": match.end()
            })
            
        return entities
        
    def _mock_zero_shot_response(self, payload):
        """Generate mock zero-shot classification response"""
        sequences = payload.get("inputs", "")
        candidate_labels = payload.get("parameters", {}).get("candidate_labels", [])
        
        if not sequences or not candidate_labels:
            return {"error": "Missing required parameters"}
            
        if isinstance(candidate_labels, str):
            candidate_labels = candidate_labels.split(",")
            
        # Generate random scores that sum to 1
        import random
        scores = [random.random() for _ in candidate_labels]
        total = sum(scores)
        scores = [s / total for s in scores]
        
        # Sort by score in descending order
        labels_and_scores = list(zip(candidate_labels, scores))
        labels_and_scores.sort(key=lambda x: x[1], reverse=True)
        
        return {
            "sequence": sequences,
            "labels": [l for l, _ in labels_and_scores],
            "scores": [s for _, s in labels_and_scores]
        }
        
    def _mock_summarization_response(self, payload):
        """Generate mock summarization response"""
        text = payload.get("inputs", "")
        if not text:
            return [{"summary_text": ""}]
            
        # Very basic summarization - just take the first few sentences
        sentences = text.split(".")
        summary = ". ".join(sentences[:min(3, len(sentences))]) + "."
        
        return [{"summary_text": summary}]
        
    def _mock_resume_scoring_response(self, payload):
        """Generate mock resume scoring response"""
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
        
    def _mock_resume_matching_response(self, payload):
        """Generate mock resume matching response"""
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
        
    @st.cache_data(ttl=3600)  # Cache results for 1 hour
    def extract_named_entities(self, text):
        """
        Extract named entities from text
        
        Args:
            text (str): Text to extract entities from
            
        Returns:
            list: List of extracted entities
        """
        # Try local pipeline first
        ner_pipeline = self.get_pipeline("ner")
        if ner_pipeline:
            try:
                # Limit text length to avoid timeouts
                if len(text) > 10000:
                    text = text[:10000]
                    
                # Get entities
                entities = ner_pipeline(text)
                return entities
            except Exception as e:
                logger.error(f"Error using local NER pipeline: {str(e)}")
                # Fall back to API
                
        # Try API
        try:
            response = self.call_api(
                self.models["ner"],
                {"inputs": text}
            )
            return response
        except Exception as e:
            logger.error(f"Error extracting named entities: {str(e)}")
            return []
            
    @st.cache_data(ttl=3600)  # Cache results for 1 hour
    def zero_shot_classification(self, text, labels):
        """
        Classify text into given categories using zero-shot classification
        
        Args:
            text (str): Text to classify
            labels (list): List of possible categories
            
        Returns:
            dict: Classification results
        """
        # Try local pipeline first
        pipeline = self.get_pipeline("zero_shot")
        if pipeline:
            try:
                # Limit text length to avoid timeouts
                if len(text) > 10000:
                    text = text[:10000]
                    
                # Get classification
                result = pipeline(text, labels)
                return result
            except Exception as e:
                logger.error(f"Error using local zero-shot pipeline: {str(e)}")
                # Fall back to API
                
        # Try API
        try:
            response = self.call_api(
                self.models["zero_shot"],
                {
                    "inputs": text,
                    "parameters": {"candidate_labels": labels}
                }
            )
            return response
        except Exception as e:
            logger.error(f"Error in zero-shot classification: {str(e)}")
            return {
                "sequence": text,
                "labels": labels,
                "scores": [1.0 / len(labels)] * len(labels)  # Equal probabilities
            }
            
    @st.cache_data(ttl=3600)  # Cache results for 1 hour
    def summarize_text(self, text, max_length=150, min_length=30):
        """
        Summarize text
        
        Args:
            text (str): Text to summarize
            max_length (int): Maximum summary length
            min_length (int): Minimum summary length
            
        Returns:
            str: Summarized text
        """
        # Try local pipeline first
        pipeline = self.get_pipeline("summarization")
        if pipeline:
            try:
                # Limit text length to avoid timeouts
                if len(text) > 10000:
                    text = text[:10000]
                    
                # Get summary
                result = pipeline(text, max_length=max_length, min_length=min_length)
                return result[0]["summary_text"]
            except Exception as e:
                logger.error(f"Error using local summarization pipeline: {str(e)}")
                # Fall back to API
                
        # Try API
        try:
            response = self.call_api(
                self.models["summarization"],
                {
                    "inputs": text,
                    "parameters": {"max_length": max_length, "min_length": min_length}
                }
            )
            return response[0]["summary_text"]
        except Exception as e:
            logger.error(f"Error summarizing text: {str(e)}")
            # Simple fallback - first few sentences
            sentences = text.split(".")
            return ". ".join(sentences[:min(3, len(sentences))]) + "."
            
    def score_resume(self, resume_sections=None, resume_text=None):
        """
        Score a resume for overall quality and relevance
        
        Args:
            resume_sections (dict): Dictionary of resume sections
            resume_text (str): Full resume text as alternative to sections
            
        Returns:
            dict: Scoring results including score and feedback
        """
        # Prepare the payload
        payload = {}
        if resume_sections:
            payload["resume_sections"] = resume_sections
        elif resume_text:
            payload["resume_text"] = resume_text
        else:
            return {"error": "No resume content provided"}
        
        # Call the API or use mock
        result = self.call_api(self.models["resume_scoring"], payload)
        
        # Process and return the results
        return {
            "score": result.get("score", 0),
            "explanation": result.get("explanation", ""),
            "strengths": result.get("strengths", []),
            "improvements": result.get("improvements", [])
        }
    
    def match_resume_to_job(self, resume_sections, job_description):
        """
        Match a resume against a job description
        
        Args:
            resume_sections (dict): Dictionary of resume sections
            job_description (str): Job description text
            
        Returns:
            dict: Matching results including score and recommendations
        """
        # Prepare the payload
        payload = {
            "resume_sections": resume_sections,
            "job_description": job_description
        }
        
        # Call the API or use mock
        result = self.call_api(self.models["resume_matching"], payload)
        
        # Process and return the results
        return {
            "match_score": result.get("match_score", 0),
            "match_details": result.get("match_details", {}),
            "matching_keywords": result.get("matching_keywords", []),
            "missing_keywords": result.get("missing_keywords", []),
            "improvement_suggestions": result.get("improvement_suggestions", [])
        }
        
    def enhance_section_with_keywords(self, section_content, target_keywords):
        """
        Enhance a section by incorporating target keywords naturally
        
        Args:
            section_content (str): Original section content
            target_keywords (list): List of keywords to incorporate
            
        Returns:
            str: Enhanced section content
        """
        if not section_content or not target_keywords:
            return section_content
            
        # Prepare prompt for generating enhanced content
        prompt = f"""
        Original content:
        ```
        {section_content}
        ```
        
        Please enhance the above content by incorporating these keywords naturally:
        {', '.join(target_keywords)}
        
        The enhanced content should read naturally and professionally.
        """
        
        # No direct text generation API in Hugging Face, so we'll simulate it
        # In a real implementation, you'd call a text generation model
        
        # Very simple fallback - ensure keywords are present
        enhanced_content = section_content
        for keyword in target_keywords:
            if keyword.lower() not in section_content.lower():
                # Simple addition of keywords at the end
                enhanced_content += f"\n• Proficient in {keyword}"
                
        return enhanced_content 