"""
Resume processing utilities for text extraction and analysis
"""

import os
import re
import logging
from typing import Dict, List, Any, Tuple, Optional

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract text from a PDF file using multiple methods for reliability
    
    Args:
        pdf_path (str): Path to the PDF file
        
    Returns:
        str: Extracted text from the PDF
    """
    try:
        # Try using PyPDF2 first
        try:
            import PyPDF2
            
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page_num in range(len(pdf_reader.pages)):
                    text += pdf_reader.pages[page_num].extract_text() + "\n"
                
                if text.strip():
                    logger.info(f"Successfully extracted {len(text)} chars with PyPDF2")
                    return text
        except (ImportError, Exception) as e:
            logger.warning(f"PyPDF2 extraction failed: {str(e)}")
        
        # Try using pdfminer as backup
        try:
            from pdfminer.high_level import extract_text as pdfminer_extract
            
            text = pdfminer_extract(pdf_path)
            if text.strip():
                logger.info(f"Successfully extracted {len(text)} chars with pdfminer")
                return text
        except (ImportError, Exception) as e:
            logger.warning(f"pdfminer extraction failed: {str(e)}")
        
        # Try using textract as last resort
        try:
            import textract
            
            text = textract.process(pdf_path).decode('utf-8')
            if text.strip():
                logger.info(f"Successfully extracted {len(text)} chars with textract")
                return text
        except (ImportError, Exception) as e:
            logger.warning(f"textract extraction failed: {str(e)}")
        
        # If all methods fail, raise exception
        raise Exception("All PDF extraction methods failed")
    
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {str(e)}")
        # Return empty string if all extraction methods fail
        return ""

def extract_text_advanced(pdf_path: str) -> Tuple[str, Dict[str, Any]]:
    """
    Enhanced text extraction with metadata
    
    Args:
        pdf_path (str): Path to the PDF file
        
    Returns:
        tuple: (extracted_text, metadata)
    """
    # Start with basic extraction
    text = extract_text_from_pdf(pdf_path)
    
    # Collect metadata
    metadata = {
        "extraction_method": "advanced",
        "char_count": len(text),
        "word_count": len(text.split()),
        "line_count": len(text.splitlines())
    }
    
    return text, metadata

def extract_structured_data(text: str) -> Dict[str, Any]:
    """
    Extract structured data from resume text using regex patterns
    
    Args:
        text (str): The resume text
        
    Returns:
        dict: Dictionary with extracted sections
    """
    # Initialize structured data dictionary
    structured_data = {
        "full_text": text
    }
    
    # Extract personal information
    personal_info = extract_personal_info(text)
    if personal_info:
        structured_data["personal_info"] = personal_info
    
    # Extract sections based on common resume section titles
    sections = {
        "objective_summary": extract_section(text, ["objective", "summary", "profile", "about me"]),
        "education": extract_section(text, ["education", "academic background", "qualifications"]),
        "experience": extract_section(text, ["experience", "work history", "employment", "professional experience"]),
        "skills": extract_section(text, ["skills", "technical skills", "competencies", "proficiencies"]),
        "certifications": extract_section(text, ["certifications", "certificates", "accreditations"]),
        "projects": extract_section(text, ["projects", "project experience", "key projects"]),
        "awards": extract_section(text, ["awards", "honors", "achievements", "recognition"]),
    }
    
    # Add non-empty sections to the result
    for section_name, section_content in sections.items():
        if section_content:
            structured_data[section_name] = section_content
    
    return structured_data

def extract_structured_data_advanced(text: str) -> Dict[str, Any]:
    """
    Enhanced structured data extraction using advanced techniques
    
    Args:
        text (str): The resume text
        
    Returns:
        dict: Dictionary with extracted sections and more detailed structure
    """
    # Start with basic extraction
    structured_data = extract_structured_data(text)
    
    # Try to further structure the data
    try:
        # Parse education into a list of education entries
        if "education" in structured_data:
            education_entries = parse_education_section(structured_data["education"])
            structured_data["education"] = education_entries
        
        # Parse work experience into a list of job entries
        if "experience" in structured_data:
            experience_entries = parse_experience_section(structured_data["experience"])
            structured_data["work_experience"] = experience_entries
            # Keep original text as backup
            structured_data["experience_raw"] = structured_data["experience"]
            
        # Parse skills into a list
        if "skills" in structured_data:
            skills_list = parse_skills_section(structured_data["skills"])
            structured_data["skills"] = skills_list
    except Exception as e:
        logger.error(f"Error in advanced structured data extraction: {str(e)}")
    
    return structured_data

def extract_personal_info(text: str) -> Dict[str, str]:
    """
    Extract personal information (name, email, phone, etc.) from resume text
    
    Args:
        text (str): The resume text
        
    Returns:
        dict: Dictionary with personal information
    """
    personal_info = {}
    
    # Extract email
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    email_matches = re.findall(email_pattern, text)
    if email_matches:
        personal_info["email"] = email_matches[0]
    
    # Extract phone number
    phone_pattern = r'\b(?:\+\d{1,3}[- ]?)?\(?\d{3}\)?[- ]?\d{3}[- ]?\d{4}\b'
    phone_matches = re.findall(phone_pattern, text)
    if phone_matches:
        personal_info["phone"] = phone_matches[0]
    
    # Extract LinkedIn profile
    linkedin_pattern = r'linkedin\.com/in/[A-Za-z0-9_-]+'
    linkedin_matches = re.findall(linkedin_pattern, text.lower())
    if linkedin_matches:
        personal_info["linkedin"] = linkedin_matches[0]
    
    # Extract name (best guess - first line or first capitalized words)
    lines = text.strip().split('\n')
    if lines:
        # Assume name is in the first line
        potential_name = lines[0].strip()
        # Check if it looks like a name (no typical section titles, etc.)
        if potential_name and len(potential_name.split()) <= 4 and not any(keyword in potential_name.lower() for keyword in ["resume", "cv", "curriculum"]):
            personal_info["name"] = potential_name
    
    return personal_info

def extract_section(text: str, keywords: List[str]) -> str:
    """
    Extract a section from resume text based on section title keywords
    
    Args:
        text (str): The resume text
        keywords (list): List of possible section title keywords
        
    Returns:
        str: Extracted section content
    """
    # Convert text to lowercase for case-insensitive matching
    text_lower = text.lower()
    lines = text.split('\n')
    
    # Find potential section headings
    for i, line in enumerate(lines):
        line_lower = line.lower().strip()
        
        # Check if line contains any of the keywords as a standalone title
        if any(keyword in line_lower for keyword in keywords) and len(line_lower.split()) <= 5:
            # Found a potential section heading, now extract content until the next section
            start_idx = i + 1
            end_idx = len(lines)
            
            # Find the end of this section (start of next section)
            for j in range(start_idx, len(lines)):
                # Look for the next section heading (capitalized short line)
                if lines[j].strip() and lines[j].strip()[0].isupper() and len(lines[j].strip().split()) <= 5:
                    # Check if it's a common section heading
                    if any(heading in lines[j].lower() for heading in [
                        "education", "experience", "skills", "certifications", 
                        "projects", "awards", "publications", "references", 
                        "summary", "objective", "contact"
                    ]):
                        end_idx = j
                        break
            
            # Extract the section content
            section_content = '\n'.join(lines[start_idx:end_idx]).strip()
            return section_content
    
    # Section not found
    return ""

def parse_education_section(education_text: str) -> List[Dict[str, str]]:
    """
    Parse education section into structured entries
    
    Args:
        education_text (str): The education section text
        
    Returns:
        list: List of education entries (dict with institution, degree, date)
    """
    education_entries = []
    
    # Split into entries (assumed to be separated by newlines)
    entries = re.split(r'\n\s*\n', education_text)
    
    for entry in entries:
        if not entry.strip():
            continue
        
        education_entry = {}
        lines = entry.strip().split('\n')
        
        # First line usually contains institution
        if lines:
            education_entry["institution"] = lines[0].strip()
        
        # Look for degree and date
        degree_pattern = r'(?:B\.?S\.?|M\.?S\.?|Ph\.?D\.?|Bachelor|Master|Doctor|MBA|Associate)'
        date_pattern = r'(?:19|20)\d{2}(?:\s*-\s*(?:19|20)\d{2}|(?:\s*-\s*)?Present|Current)?'
        
        for line in lines[1:]:
            # Look for degree
            degree_match = re.search(degree_pattern, line)
            if degree_match and "degree" not in education_entry:
                # Extract the degree and possibly more context
                degree_context = line.strip()
                education_entry["degree"] = degree_context
            
            # Look for date
            date_match = re.search(date_pattern, line)
            if date_match and "date" not in education_entry:
                education_entry["date"] = date_match.group(0)
        
        if education_entry:
            education_entries.append(education_entry)
    
    return education_entries

def parse_experience_section(experience_text: str) -> List[Dict[str, str]]:
    """
    Parse work experience section into structured entries
    
    Args:
        experience_text (str): The work experience section text
        
    Returns:
        list: List of job entries (dict with company, title, duration, description)
    """
    experience_entries = []
    
    # Split into entries (assumed to be separated by newlines)
    entries = re.split(r'\n\s*\n', experience_text)
    
    for entry in entries:
        if not entry.strip():
            continue
        
        experience_entry = {}
        lines = entry.strip().split('\n')
        
        # First line usually contains company or title
        if lines:
            if any(title in lines[0].lower() for title in ["engineer", "developer", "manager", "director", "analyst"]):
                experience_entry["title"] = lines[0].strip()
            else:
                experience_entry["company"] = lines[0].strip()
        
        # Look for company name, job title, and duration
        company_pattern = r'(?:at|with|for)?\s*([A-Z][A-Za-z0-9\s\.&,]+)'
        title_pattern = r'(?:as|as a|as an)?\s*([A-Z][A-Za-z\s]+(?:Engineer|Developer|Manager|Director|Analyst|Designer|Architect))'
        date_pattern = r'(?:19|20)\d{2}(?:\s*-\s*(?:19|20)\d{2}|(?:\s*-\s*)?Present|Current)?'
        
        for i, line in enumerate(lines[1:3]):  # Check first few lines for metadata
            # Look for company
            if "company" not in experience_entry:
                company_match = re.search(company_pattern, line)
                if company_match:
                    experience_entry["company"] = company_match.group(1).strip()
            
            # Look for title
            if "title" not in experience_entry:
                title_match = re.search(title_pattern, line)
                if title_match:
                    experience_entry["title"] = title_match.group(1).strip()
            
            # Look for duration
            if "duration" not in experience_entry:
                date_match = re.search(date_pattern, line)
                if date_match:
                    experience_entry["duration"] = date_match.group(0)
        
        # Rest is description
        description_start_idx = 1
        if "title" in experience_entry and "company" in experience_entry and "duration" in experience_entry:
            description_start_idx = 3  # Skip metadata lines
        elif "title" in experience_entry or "company" in experience_entry:
            description_start_idx = 2  # Skip one metadata line
        
        if len(lines) > description_start_idx:
            experience_entry["description"] = '\n'.join(lines[description_start_idx:]).strip()
        
        if experience_entry:
            experience_entries.append(experience_entry)
    
    return experience_entries

def parse_skills_section(skills_text: str) -> List[str]:
    """
    Parse skills section into a list of individual skills
    
    Args:
        skills_text (str): The skills section text
        
    Returns:
        list: List of individual skills
    """
    skills = []
    
    # Look for skills listed with bullets, commas, or newlines
    skills_text = skills_text.replace('•', ',').replace('●', ',').replace('○', ',').replace('■', ',')
    
    # Split by common separators
    for item in re.split(r',|\n', skills_text):
        skill = item.strip()
        if skill and len(skill) > 1:  # Filter out single characters and empty strings
            skills.append(skill)
    
    return skills

def generate_confidence_scores(resume_sections: Dict[str, Any]) -> Dict[str, int]:
    """
    Generate confidence scores for resume sections
    
    Args:
        resume_sections (dict): Dictionary of resume sections
        
    Returns:
        dict: Dictionary with confidence scores for each section
    """
    confidence_scores = {}
    
    # Define score calculation rules per section
    for section, content in resume_sections.items():
        if section == "full_text":
            continue
        
        # Base confidence score
        score = 50
        
        # Skip empty sections
        if not content:
            confidence_scores[section] = 0
            continue
        
        # Calculate score based on content
        if isinstance(content, str):
            # For string content, check length and quality
            content_length = len(content)
            if content_length > 500:
                score += 30
            elif content_length > 200:
                score += 20
            elif content_length > 100:
                score += 10
            
            # Check for bullet points (indication of well-structured content)
            if '•' in content or '*' in content or '-' in content:
                score += 10
        
        elif isinstance(content, list):
            # For list content, check number of items
            if len(content) > 10:
                score += 30
            elif len(content) > 5:
                score += 20
            elif len(content) > 2:
                score += 10
            
            # Check content quality for each item
            for item in content:
                if isinstance(item, dict) and len(item) >= 3:
                    score += 5  # Well-structured item with multiple fields
        
        elif isinstance(content, dict):
            # For dict content, check number of fields
            if len(content) > 5:
                score += 30
            elif len(content) > 3:
                score += 20
            elif len(content) > 1:
                score += 10
        
        # Ensure score is within range
        confidence_scores[section] = min(max(score, 0), 100)
    
    # Set sections to more readable names
    readable_scores = {}
    name_mapping = {
        "personal_info": "Personal Info",
        "objective_summary": "Summary",
        "education": "Education",
        "experience": "Experience",
        "work_experience": "Work Experience",
        "skills": "Skills",
        "certifications": "Certifications",
        "projects": "Projects",
        "awards": "Awards"
    }
    
    for section, score in confidence_scores.items():
        readable_name = name_mapping.get(section, section.replace("_", " ").title())
        readable_scores[readable_name] = score
    
    # Add overall score
    if readable_scores:
        readable_scores["Overall"] = sum(readable_scores.values()) // len(readable_scores)
    else:
        readable_scores["Overall"] = 0
    
    return readable_scores

def find_missing_sections(resume_sections: Dict[str, Any]) -> List[str]:
    """
    Identify missing resume sections
    
    Args:
        resume_sections (dict): Dictionary of resume sections
        
    Returns:
        list: List of missing section names
    """
    # Define essential sections
    essential_sections = [
        "summary", "objective_summary", "objective", 
        "experience", "work_experience", 
        "education", 
        "skills"
    ]
    
    missing_sections = []
    
    for section in essential_sections:
        # Check if any variation of the section exists
        found = False
        for existing_section in resume_sections:
            if section in existing_section.lower():
                found = True
                break
        
        if not found:
            # Convert to user-friendly name
            user_friendly_name = section.replace("_", " ").title()
            missing_sections.append(user_friendly_name)
    
    # Remove duplicates (e.g. Summary vs Objective Summary)
    final_missing = []
    if "Summary" in missing_sections and "Objective Summary" in missing_sections:
        final_missing.append("Summary/Objective")
    else:
        if "Summary" in missing_sections:
            final_missing.append("Summary")
        if "Objective Summary" in missing_sections:
            final_missing.append("Objective")
    
    # Add other missing sections
    for section in missing_sections:
        if section not in ["Summary", "Objective Summary"]:
            final_missing.append(section)
    
    return final_missing

def check_grammar(text: str) -> List[Dict[str, str]]:
    """
    Basic grammar checking for resume text
    
    Args:
        text (str): The resume text
        
    Returns:
        list: List of grammar issues (dicts with text, suggestion, reason)
    """
    issues = []
    
    # Very basic grammar checks
    
    # Check for common spelling errors
    spelling_errors = {
        "recieve": "receive",
        "acheive": "achieve",
        "accomodate": "accommodate",
        "adress": "address",
        "advertisment": "advertisement",
        "beleive": "believe",
        "bizness": "business",
        "calender": "calendar",
        "catagory": "category",
        "cemetary": "cemetery",
        "collegue": "colleague",
        "comming": "coming",
        "commitee": "committee",
        "completly": "completely",
        "concious": "conscious",
        "curiousity": "curiosity",
        "definately": "definitely",
        "dissapoint": "disappoint",
        "embarass": "embarrass",
        "enviroment": "environment",
        "excellant": "excellent",
        "facinating": "fascinating",
        "familar": "familiar",
        "finaly": "finally",
        "flourescent": "fluorescent",
        "foriegn": "foreign",
        "freind": "friend",
        "garantee": "guarantee",
        "glamourous": "glamorous",
        "goverment": "government",
        "happyness": "happiness",
        "harrassment": "harassment",
        "immediatly": "immediately",
        "independant": "independent",
        "jist": "gist",
        "knowlege": "knowledge",
        "liason": "liaison",
        "libary": "library",
        "lisence": "license",
        "maintainance": "maintenance",
        "millenium": "millennium",
        "momento": "memento",
        "neccessary": "necessary",
        "occassion": "occasion",
        "occured": "occurred",
        "paralel": "parallel",
        "personalyy": "personally",
        "posession": "possession",
        "prefered": "preferred",
        "priviledge": "privilege",
        "publically": "publicly",
        "realy": "really",
        "recieve": "receive",
        "recomend": "recommend",
        "refered": "referred",
        "relevent": "relevant",
        "religous": "religious",
        "remeber": "remember",
        "seperate": "separate",
        "seige": "siege",
        "succesful": "successful",
        "surprize": "surprise",
        "unforseen": "unforeseen",
        "unfortunatly": "unfortunately",
        "untill": "until",
        "wierd": "weird"
    }
    
    for word, correct in spelling_errors.items():
        pattern = r'\b' + word + r'\b'
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            issues.append({
                "text": match.group(0),
                "suggestion": correct,
                "reason": f"Spelling error: '{match.group(0)}' should be '{correct}'"
            })
    
    # Check for double spaces
    double_space_pattern = r'[^.!?]  +[A-Za-z]'
    matches = re.finditer(double_space_pattern, text)
    for match in matches:
        full_match = match.group(0)
        corrected = re.sub(r'  +', ' ', full_match)
        issues.append({
            "text": full_match,
            "suggestion": corrected,
            "reason": "Double space found, use single space"
        })
    
    # Check for common capitalization issues
    sent_start_pattern = r'[.!?]\s+[a-z]'
    matches = re.finditer(sent_start_pattern, text)
    for match in matches:
        full_match = match.group(0)
        corrected = full_match[:-1] + full_match[-1].upper()
        issues.append({
            "text": full_match,
            "suggestion": corrected,
            "reason": "Sentence should start with a capital letter"
        })
    
    return issues

def extract_keywords_from_text(text: str, max_keywords: int = 20) -> List[str]:
    """
    Extract keywords from text
    
    Args:
        text (str): The text to extract keywords from
        max_keywords (int): Maximum number of keywords to return
        
    Returns:
        list: List of keywords
    """
    # Common resume keywords
    resume_keywords = [
        "achieved", "improved", "developed", "managed", "created", "resolved",
        "delivered", "led", "organized", "designed", "implemented", "reduced",
        "increased", "negotiated", "coordinated", "leadership", "teamwork",
        "communication", "problem-solving", "analytical", "strategic", "planning",
        "project management", "budget", "sales", "marketing", "research",
        "customer service", "operations", "technical", "programming", "software",
        "hardware", "network", "database", "web", "mobile", "cloud", "security",
        "analysis", "testing", "quality assurance", "agile", "scrum", "lean",
        "six sigma", "ISO", "compliance", "regulation", "policy", "procedure",
        "training", "mentoring", "coaching", "presentations", "reports",
        "documentation", "specifications", "requirements", "architecture", "design",
        "development", "implementation", "deployment", "maintenance", "support",
        "troubleshooting", "debugging", "optimization", "performance",
        "scalability", "reliability", "availability", "security", "usability"
    ]
    
    # Extract potential keywords from text
    words = re.findall(r'\b[A-Za-z][A-Za-z-]+\b', text.lower())
    
    # Count word frequency
    word_count = {}
    for word in words:
        if word not in word_count:
            word_count[word] = 0
        word_count[word] += 1
    
    # Filter out common words
    common_words = ["the", "and", "to", "of", "a", "in", "for", "on", "with", "at", "by", "from", "is", "was", "were", "are", "be", "been", "being", "have", "has", "had", "do", "does", "did", "can", "could", "will", "would", "shall", "should", "may", "might", "must"]
    for word in common_words:
        if word in word_count:
            del word_count[word]
    
    # Sort by frequency and filter for resume keywords or minimum length
    keywords = []
    sorted_words = sorted(word_count.items(), key=lambda x: x[1], reverse=True)
    
    for word, count in sorted_words:
        if word in resume_keywords or count > 2 or len(word) > 6:
            keywords.append(word)
        
        if len(keywords) >= max_keywords:
            break
    
    return keywords

def find_improvement_suggestions(text: str, job_description: str = "") -> List[Dict[str, str]]:
    """
    Find improvement suggestions for resume text
    
    Args:
        text (str): The resume text
        job_description (str): Optional job description for targeted suggestions
        
    Returns:
        list: List of improvement suggestions
    """
    suggestions = []
    
    # Check for weak phrases
    weak_phrases = {
        "responsible for": "Led, Managed, Oversaw, Directed, Coordinated",
        "duties included": "Achievements included, Delivered, Executed",
        "worked on": "Developed, Created, Built, Implemented",
        "helped with": "Contributed to, Supported, Assisted in, Collaborated on",
        "was tasked with": "Spearheaded, Championed, Executed",
        "participated in": "Contributed to, Collaborated on, Partnered in",
        "was involved in": "Drove, Led, Guided, Directed",
        "assisted in": "Supported, Contributed to, Facilitated",
        "in charge of": "Managed, Led, Directed, Oversaw",
        "worked with": "Collaborated with, Partnered with, Teamed with"
    }
    
    for phrase, replacements in weak_phrases.items():
        pattern = r'\b' + re.escape(phrase) + r'\b'
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            suggestions.append({
                "text": match.group(0),
                "suggestion": f"Replace '{match.group(0)}' with stronger action verbs like: {replacements}",
                "reason": f"Weak phrase detected. Use stronger action verbs for more impact.",
                "section": "Experience"
            })
    
    # Check for numeric achievements
    if "percent" in text.lower() or "percentage" in text.lower():
        if not re.search(r'\d+%', text) and not re.search(r'\d+ percent', text):
            suggestions.append({
                "text": "percentage achievement",
                "suggestion": "Quantify achievements with specific percentages (e.g., 'increased productivity by 25%')",
                "reason": "Vague mention of percentage without specific numbers",
                "section": "Experience"
            })
    
    # Check for summary section quality
    summary_section = extract_section(text, ["summary", "profile", "objective"])
    if summary_section:
        # Check length
        if len(summary_section.split()) < 50:
            suggestions.append({
                "text": summary_section,
                "suggestion": "Expand your summary to include key achievements, skills, and value proposition",
                "reason": "Summary section is too brief",
                "section": "Summary"
            })
        # Check for first-person pronouns
        if re.search(r'\bI\b|\bmy\b|\bme\b', summary_section):
            suggestions.append({
                "text": summary_section,
                "suggestion": "Remove first-person pronouns (I, my, me) from summary section",
                "reason": "Professional summaries typically avoid first-person pronouns",
                "section": "Summary"
            })
    
    # If job description is provided, check for keyword alignment
    if job_description:
        job_keywords = extract_keywords_from_text(job_description, 15)
        resume_keywords = extract_keywords_from_text(text, 30)
        
        missing_keywords = [keyword for keyword in job_keywords if keyword not in resume_keywords]
        if missing_keywords:
            suggestions.append({
                "text": "Missing job keywords",
                "suggestion": f"Consider incorporating these keywords from the job description: {', '.join(missing_keywords)}",
                "reason": "Your resume is missing key terms from the job description",
                "section": "Skills"
            })
    
    return suggestions 