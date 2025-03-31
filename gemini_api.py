import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure the Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

class GeminiProcessor:
    """Class to handle interactions with the Gemini API"""
    
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-pro')
    
    def extract_resume_sections(self, resume_text):
        """
        Extract key sections from a resume
        
        Args:
            resume_text: The text content of the resume
        
        Returns:
            dict: Dictionary with extracted sections
        """
        prompt = f"""
        Extract the following information from the resume text below. 
        For each section, return the content if present. If a section is not present, return "Missing".
        
        Sections to extract:
        1. Personal Information (name, email, phone, LinkedIn, GitHub, etc.)
        2. Objective/Resume Summary
        3. Education
        4. Skills
        5. Work Experience
        6. Certifications
        7. Projects
        8. Awards and Honors
        9. Publications
        10. Languages
        11. Professional Affiliations
        
        Resume Text:
        {resume_text}
        
        Return the extracted information in a structured format.
        """
        
        response = self.model.generate_content(prompt)
        
        # Process the response into a structured dictionary
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
        
        # Parse the response text to extract section content
        # This is a simplified placeholder - proper parsing would be implemented here
        response_text = response.text
        
        # Example parsing (would need to be improved based on actual Gemini response format)
        current_section = None
        section_content = ""
        
        for line in response_text.split("\n"):
            line = line.strip()
            if not line:
                continue
                
            # Check if this line is a section header
            section_match = None
            for section in extracted_sections.keys():
                if section.lower() in line.lower() and ":" in line:
                    section_match = section
                    break
            
            if section_match:
                # Save previous section content
                if current_section:
                    extracted_sections[current_section] = section_content.strip()
                
                # Start new section
                current_section = section_match
                section_content = line.split(":", 1)[1].strip()
            elif current_section:
                section_content += " " + line
        
        # Save the last section
        if current_section and section_content:
            extracted_sections[current_section] = section_content.strip()
            
        return extracted_sections
    
    def calculate_resume_scores(self, resume_sections):
        """
        Calculate GenAI and AI scores based on resume content
        
        Args:
            resume_sections: Dictionary with extracted resume sections
        
        Returns:
            dict: Dictionary with GenAI and AI scores
        """
        prompt = f"""
        Evaluate the resume content below for relevance to GenAI and AI fields.
        
        GenAI Score (0-100) should assess:
        - Presence of Generative AI terms (GANs, VAEs, diffusion models, transformers)
        - LLM experience (GPT, BERT, fine-tuning, prompt engineering)
        - Relevant tools (PyTorch, Hugging Face, Stable Diffusion)
        - Associated concepts (synthetic data generation, model interpretability)
        
        AI Score (0-100) should assess:
        - Machine Learning concepts (regression, classification, clustering)
        - Deep Learning experience (CNNs, RNNs, neural networks)
        - NLP concepts (tokenization, sentiment analysis, embeddings)
        - Relevant tools (TensorFlow, Scikit-learn, Keras)
        - Associated concepts (model evaluation, overfitting, optimization)
        
        Resume Content:
        {resume_sections}
        
        For each score, provide:
        1. The numerical score (0-100)
        2. A short explanation of the score
        3. A list of strengths
        4. A list of areas for improvement
        
        Return results in a structured format.
        """
        
        response = self.model.generate_content(prompt)
        
        # Process the response into a structured dictionary
        # This is a simplified implementation - would need better parsing in production
        scores = {
            "GenAI": {
                "score": 0,
                "explanation": "",
                "strengths": [],
                "improvements": []
            },
            "AI": {
                "score": 0,
                "explanation": "",
                "strengths": [],
                "improvements": []
            }
        }
        
        # Parse the response to extract scores and details
        response_text = response.text
        
        # Example parsing logic (needs to be customized based on actual response format)
        current_section = None
        for line in response_text.split("\n"):
            line = line.strip()
            if not line:
                continue
                
            if "genai score" in line.lower() or "gen ai score" in line.lower():
                current_section = "GenAI"
                # Extract score if present (e.g., "GenAI Score: 65/100")
                if ":" in line and any(char.isdigit() for char in line):
                    score_text = line.split(":", 1)[1].strip()
                    scores["GenAI"]["score"] = int(''.join(filter(str.isdigit, score_text)))
            elif "ai score" in line.lower():
                current_section = "AI"
                # Extract score if present
                if ":" in line and any(char.isdigit() for char in line):
                    score_text = line.split(":", 1)[1].strip()
                    scores["AI"]["score"] = int(''.join(filter(str.isdigit, score_text)))
            elif current_section and "strengths" in line.lower():
                # Next lines will be strengths
                continue
            elif current_section and "improvements" in line.lower() or "areas for improvement" in line.lower():
                # Next lines will be improvements
                continue
            elif current_section and line.startswith("- "):
                # This is a bullet point
                if "strengths" in response_text.split(line)[0].lower().split("\n")[-2].lower():
                    scores[current_section]["strengths"].append(line[2:])
                elif "improvements" in response_text.split(line)[0].lower().split("\n")[-2].lower() or "areas for improvement" in response_text.split(line)[0].lower().split("\n")[-2].lower():
                    scores[current_section]["improvements"].append(line[2:])
            elif current_section and not scores[current_section]["explanation"] and "score" not in line.lower() and ":" not in line:
                # This might be the explanation
                scores[current_section]["explanation"] = line
        
        return scores
    
    def enhance_resume(self, resume_sections, scores):
        """
        Generate enhancements for a resume based on sections and scores
        
        Args:
            resume_sections: Dictionary with extracted resume sections
            scores: Dictionary with GenAI and AI scores
        
        Returns:
            dict: Dictionary with enhanced sections
        """
        prompt = f"""
        Enhance the following resume sections to improve their relevance to GenAI and AI fields.
        
        Current GenAI Score: {scores['GenAI']['score']}/100
        Current AI Score: {scores['AI']['score']}/100
        
        Areas for improvement in GenAI: {', '.join(scores['GenAI']['improvements'])}
        Areas for improvement in AI: {', '.join(scores['AI']['improvements'])}
        
        For each section, provide an enhanced version that:
        1. Improves clarity and impact
        2. Naturally integrates relevant keywords
        3. Quantifies achievements where possible
        4. Follows best practices for technical resumes
        
        Resume Sections:
        {resume_sections}
        
        For each section, return both the original content and enhanced version.
        """
        
        response = self.model.generate_content(prompt)
        
        # Process the response to extract enhanced sections
        enhanced_sections = {}
        
        # Parse the response to extract enhancements for each section
        # This is a simplified implementation - would need better parsing in production
        response_text = response.text
        
        current_section = None
        is_original = True
        original_content = ""
        enhanced_content = ""
        
        for line in response_text.split("\n"):
            line = line.strip()
            if not line:
                continue
                
            # Check if this is a section header
            section_match = None
            for section in resume_sections.keys():
                if section.lower() in line.lower() and ":" in line:
                    section_match = section
                    break
            
            if section_match:
                # Save previous section content
                if current_section and original_content and enhanced_content:
                    enhanced_sections[current_section] = {
                        "original": original_content.strip(),
                        "enhanced": enhanced_content.strip()
                    }
                
                # Start new section
                current_section = section_match
                original_content = ""
                enhanced_content = ""
                is_original = True
            elif "original" in line.lower() or "current" in line.lower():
                is_original = True
            elif "enhanced" in line.lower() or "improved" in line.lower():
                is_original = False
            elif current_section:
                if is_original:
                    original_content += " " + line
                else:
                    enhanced_content += " " + line
        
        # Save the last section
        if current_section and original_content and enhanced_content:
            enhanced_sections[current_section] = {
                "original": original_content.strip(),
                "enhanced": enhanced_content.strip()
            }
            
        return enhanced_sections
    
    def match_resume_to_job(self, resume_sections, job_description):
        """
        Calculate match score between resume and job description
        
        Args:
            resume_sections: Dictionary with extracted resume sections
            job_description: Text of the job description
        
        Returns:
            dict: Dictionary with match score and details
        """
        prompt = f"""
        Compare the resume content with the job description to calculate a match score.
        
        Evaluate the match based on:
        1. Keyword matching (overlap of terms)
        2. Skill alignment (relevance of listed skills to job requirements)
        3. Experience relevance (contextual fit of projects and roles)
        
        Resume Content:
        {resume_sections}
        
        Job Description:
        {job_description}
        
        Provide:
        1. An overall match score (0-100)
        2. A breakdown of the match (Skills: X%, Experience: Y%, etc.)
        3. Key matching strengths
        4. Key gaps or misalignments
        
        Return results in a structured format.
        """
        
        response = self.model.generate_content(prompt)
        
        # Process the response into a structured dictionary
        match_result = {
            "match_score": 0,
            "breakdown": {},
            "matching_strengths": [],
            "gaps": []
        }
        
        # Parse the response to extract match information
        response_text = response.text
        
        # Example parsing logic (needs to be customized based on actual response format)
        current_section = None
        for line in response_text.split("\n"):
            line = line.strip()
            if not line:
                continue
                
            if "match score" in line.lower() or "overall match" in line.lower():
                # Extract score if present (e.g., "Match Score: 65/100")
                if ":" in line and any(char.isdigit() for char in line):
                    score_text = line.split(":", 1)[1].strip()
                    match_result["match_score"] = int(''.join(filter(str.isdigit, score_text)))
            elif "breakdown" in line.lower() or "match breakdown" in line.lower():
                current_section = "breakdown"
            elif "matching strengths" in line.lower() or "key matching strengths" in line.lower():
                current_section = "matching_strengths"
            elif "gaps" in line.lower() or "misalignments" in line.lower():
                current_section = "gaps"
            elif current_section == "breakdown" and ":" in line:
                # Parse breakdown entries like "Skills: 75%"
                parts = line.split(":", 1)
                if len(parts) == 2 and "%" in parts[1]:
                    category = parts[0].strip()
                    score_text = parts[1].strip()
                    match_result["breakdown"][category] = int(''.join(filter(str.isdigit, score_text)))
            elif current_section in ["matching_strengths", "gaps"] and line.startswith("- "):
                # This is a bullet point
                match_result[current_section].append(line[2:])
        
        return match_result
    
    def enhance_resume_for_job(self, resume_sections, job_description, match_result):
        """
        Enhance resume to better match a specific job description
        
        Args:
            resume_sections: Dictionary with extracted resume sections
            job_description: Text of the job description
            match_result: Dictionary with match score and details
        
        Returns:
            dict: Dictionary with job-specific enhanced sections
        """
        prompt = f"""
        Enhance the resume sections to better match the following job description.
        
        Current Match Score: {match_result['match_score']}/100
        
        Key Gaps: {', '.join(match_result['gaps'])}
        
        For each section, provide an enhanced version that:
        1. Adds job-specific terms from the description
        2. Adjusts descriptions to highlight relevant experience
        3. Reorders content to prioritize job-relevant details
        4. Removes or downplays irrelevant information
        
        Resume Sections:
        {resume_sections}
        
        Job Description:
        {job_description}
        
        For each section, return both the original content and the job-tailored version.
        """
        
        response = self.model.generate_content(prompt)
        
        # Process the response to extract job-tailored sections
        job_tailored_sections = {}
        
        # Parse the response to extract enhancements for each section
        # This is a simplified implementation - would need better parsing in production
        response_text = response.text
        
        current_section = None
        is_original = True
        original_content = ""
        enhanced_content = ""
        
        for line in response_text.split("\n"):
            line = line.strip()
            if not line:
                continue
                
            # Check if this is a section header
            section_match = None
            for section in resume_sections.keys():
                if section.lower() in line.lower() and ":" in line:
                    section_match = section
                    break
            
            if section_match:
                # Save previous section content
                if current_section and original_content and enhanced_content:
                    job_tailored_sections[current_section] = {
                        "original": original_content.strip(),
                        "enhanced": enhanced_content.strip()
                    }
                
                # Start new section
                current_section = section_match
                original_content = ""
                enhanced_content = ""
                is_original = True
            elif "original" in line.lower() or "current" in line.lower():
                is_original = True
            elif "enhanced" in line.lower() or "job-tailored" in line.lower() or "tailored" in line.lower():
                is_original = False
            elif current_section:
                if is_original:
                    original_content += " " + line
                else:
                    enhanced_content += " " + line
        
        # Save the last section
        if current_section and original_content and enhanced_content:
            job_tailored_sections[current_section] = {
                "original": original_content.strip(),
                "enhanced": enhanced_content.strip()
            }
            
        return job_tailored_sections 