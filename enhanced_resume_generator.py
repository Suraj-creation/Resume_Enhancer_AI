import streamlit as st
from utils.pdf_utils import generate_enhanced_resume_pdf, generate_docx_from_pdf
import io
import base64

def generate_resume_download_buttons(enhanced_data):
    """
    Generate download buttons for resume PDF and DOCX files
    
    Args:
        enhanced_data (dict): Enhanced resume data
        
    Returns:
        tuple: (pdf_success, pdf_data, docx_data) - success flag and file data
    """
    try:
        # Generate PDF
        pdf_data = generate_enhanced_resume_pdf(enhanced_data)
        
        # Generate DOCX using the PDF data
        docx_data = generate_docx_from_pdf(pdf_data)
        
        return True, pdf_data, docx_data
    except Exception as e:
        st.error(f"Error generating resume files: {str(e)}")
        return False, None, None

def generate_resume_preview_html(enhanced_data):
    """
    Generate HTML preview of the enhanced resume
    
    Args:
        enhanced_data (dict): Enhanced resume data
        
    Returns:
        str: HTML preview of the resume
    """
    try:
        # Personal info section
        personal_info = enhanced_data.get("personal_info", {})
        name = personal_info.get("name", "Your Name")
        email = personal_info.get("email", "")
        phone = personal_info.get("phone", "")
        location = personal_info.get("location", "")
        
        # Create a contact line
        contact_parts = []
        if email:
            contact_parts.append(email)
        if phone:
            contact_parts.append(phone)
        if location:
            contact_parts.append(location)
        contact_line = " | ".join(contact_parts)
        
        # Summary
        summary = enhanced_data.get("objective_summary", "")
        
        # Generate HTML preview
        html_preview = f"""
        <div style="border: 1px solid #ccc; padding: 20px; border-radius: 5px; font-family: Arial, sans-serif;">
            <h1 style="text-align: center; color: #333; margin-bottom: 5px;">{name}</h1>
            <p style="text-align: center; color: #666; margin-bottom: 15px;">{contact_line}</p>
            <hr style="border: 0; height: 1px; background-color: #ddd; margin: 15px 0;">
        """
        
        # Summary section
        if summary:
            html_preview += f"""
            <h2 style="color: #444; font-size: 18px; margin-bottom: 10px;">SUMMARY</h2>
            <p style="color: #333; margin-bottom: 15px;">{summary}</p>
            """
        
        # Experience section
        work_experience = enhanced_data.get("work_experience", [])
        if work_experience:
            html_preview += f"""
            <h2 style="color: #444; font-size: 18px; margin-bottom: 10px;">EXPERIENCE</h2>
            """
            
            for job in work_experience:
                if isinstance(job, dict):
                    title = job.get("title", "")
                    company = job.get("company", "")
                    duration = job.get("duration", "")
                    description = job.get("description", "")
                    
                    html_preview += f"""
                    <h3 style="color: #333; font-size: 16px; margin-bottom: 5px;">{title}</h3>
                    <p style="color: #666; font-style: italic; margin-bottom: 5px;">{company} | {duration}</p>
                    """
                    
                    if description:
                        if isinstance(description, list):
                            html_preview += "<ul style='margin-top: 5px; margin-left: 20px;'>"
                            for bullet in description:
                                html_preview += f"<li style='margin-bottom: 5px;'>{bullet}</li>"
                            html_preview += "</ul>"
                        else:
                            html_preview += f"<p style='margin-bottom: 15px;'>{description}</p>"
        
        # Education section
        education = enhanced_data.get("education", [])
        if education:
            html_preview += f"""
            <h2 style="color: #444; font-size: 18px; margin-bottom: 10px;">EDUCATION</h2>
            """
            
            for edu in education:
                if isinstance(edu, dict):
                    degree = edu.get("degree", "")
                    institution = edu.get("institution", "")
                    date = edu.get("date", "")
                    
                    html_preview += f"""
                    <p style="margin-bottom: 5px;"><strong>{degree}</strong>, {institution} | {date}</p>
                    """
        
        # Skills section
        skills = enhanced_data.get("skills", [])
        if skills:
            html_preview += f"""
            <h2 style="color: #444; font-size: 18px; margin-bottom: 10px;">SKILLS</h2>
            """
            
            if isinstance(skills, dict):
                for category, skill_list in skills.items():
                    category_name = category.replace('_', ' ').title()
                    skill_text = ', '.join(skill_list)
                    html_preview += f"""
                    <p style="margin-bottom: 5px;"><strong>{category_name}:</strong> {skill_text}</p>
                    """
            elif isinstance(skills, list):
                html_preview += f"""
                <p style="margin-bottom: 15px;">{', '.join(skills)}</p>
                """
            else:
                html_preview += f"""
                <p style="margin-bottom: 15px;">{skills}</p>
                """
        
        html_preview += "</div>"
        
        return html_preview
    except Exception as e:
        return f"""
        <div style="border: 1px solid #ccc; padding: 20px; border-radius: 5px; text-align: center;">
            <p style="color: #888;">Preview unavailable: {str(e)}</p>
        </div>
        """

def get_enhanced_resume_data():
    """
    Get enhanced resume data from session state or create sample data
    
    Returns:
        dict: Enhanced resume data
    """
    if "enhanced_sections" in st.session_state and st.session_state.enhanced_sections:
        return st.session_state.enhanced_sections
    
    # If enhanced_resume exists in session state, convert to enhanced_sections format
    if "enhanced_resume" in st.session_state and st.session_state.enhanced_resume:
        # Convert enhanced_resume to enhanced_sections format
        return {
            "personal_info": {
                "name": "Your Name",
                "email": "your.email@example.com",
                "phone": "Your Phone Number",
                "location": "Your Location"
            },
            "objective_summary": st.session_state.enhanced_resume.get("summary", ""),
            "work_experience": [
                {
                    "title": "Work Experience",
                    "company": "",
                    "duration": "",
                    "description": st.session_state.enhanced_resume.get("experience", "").split("\n")
                }
            ],
            "education": [
                {
                    "degree": "Education",
                    "institution": "",
                    "date": ""
                }
            ],
            "skills": {
                "skills": st.session_state.enhanced_resume.get("skills", "").split(", ")
            },
            "additional": st.session_state.enhanced_resume.get("additional", "")
        }
    
    # If no data in session state, return a sample for testing
    return {
        "personal_info": {
            "name": "John Doe",
            "email": "john.doe@example.com",
            "phone": "(123) 456-7890",
            "location": "New York, NY"
        },
        "objective_summary": "Experienced software engineer with 5+ years of expertise in developing scalable applications using Python and JavaScript. Passionate about creating elegant solutions to complex problems.",
        "work_experience": [
            {
                "title": "Senior Software Engineer",
                "company": "Tech Solutions Inc.",
                "duration": "2020 - Present",
                "description": [
                    "Led development of a microservices architecture that improved system reliability by 45%",
                    "Managed a team of 5 engineers, mentoring junior developers and reviewing code",
                    "Implemented CI/CD pipelines that reduced deployment time by 60%"
                ]
            },
            {
                "title": "Software Developer",
                "company": "Innovation Labs",
                "duration": "2018 - 2020",
                "description": [
                    "Developed RESTful APIs for mobile and web applications",
                    "Optimized database queries resulting in 30% performance improvement",
                    "Collaborated with UX designers to implement responsive front-end components"
                ]
            }
        ],
        "education": [
            {
                "degree": "B.S. Computer Science",
                "institution": "University of Technology",
                "date": "2018"
            }
        ],
        "skills": {
            "programming_languages": ["Python", "JavaScript", "Java", "SQL"],
            "web_development": ["React", "Node.js", "HTML/CSS", "RESTful APIs"],
            "devops": ["Docker", "Kubernetes", "CI/CD", "AWS"],
            "soft_skills": ["Leadership", "Communication", "Problem Solving"]
        },
        "certifications": [
            "AWS Certified Developer Associate",
            "Certified Scrum Master"
        ],
        "projects": [
            {
                "name": "E-commerce Platform",
                "description": "Built a full-stack e-commerce solution with React and Node.js"
            }
        ]
    } 