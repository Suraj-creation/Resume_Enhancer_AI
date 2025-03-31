import os
import base64
import tempfile
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
import jinja2
import streamlit as st

# Import WeasyPrint conditionally to avoid errors if not installed
try:
    from weasyprint import HTML, CSS
    WEASYPRINT_AVAILABLE = True
except ImportError:
    WEASYPRINT_AVAILABLE = False
    st.warning("WeasyPrint is not installed. PDF generation will not work.")

# Define template directory - create if it doesn't exist
TEMPLATE_DIR = Path(__file__).parent.parent / "templates" / "resume"
TEMPLATE_DIR.mkdir(parents=True, exist_ok=True)

# Define base templates directory - this is where we store the HTML/CSS template files
STATIC_TEMPLATE_DIR = TEMPLATE_DIR / "static"
STATIC_TEMPLATE_DIR.mkdir(parents=True, exist_ok=True)

# Set up Jinja2 environment for template rendering
template_loader = jinja2.FileSystemLoader(searchpath=str(STATIC_TEMPLATE_DIR))
template_env = jinja2.Environment(loader=template_loader)

# Define the available resume templates
RESUME_TEMPLATES = {
    "modern": {
        "name": "Modern",
        "description": "Clean, professional design with a sidebar for skills and contact info",
        "preview_img": "modern_template.png",
        "template_file": "modern_template.html",
        "css_file": "modern_template.css"
    },
    "professional": {
        "name": "Professional",
        "description": "Traditional layout suitable for corporate environments",
        "preview_img": "professional_template.png",
        "template_file": "professional_template.html",
        "css_file": "professional_template.css"
    },
    "creative": {
        "name": "Creative",
        "description": "Bold, colorful design for creative industries",
        "preview_img": "creative_template.png",
        "template_file": "creative_template.html",
        "css_file": "creative_template.css"
    },
    "technical": {
        "name": "Technical",
        "description": "Code-inspired layout highlighting technical skills",
        "preview_img": "technical_template.png",
        "template_file": "technical_template.html",
        "css_file": "technical_template.css"
    },
    "executive": {
        "name": "Executive",
        "description": "Sophisticated design for senior positions",
        "preview_img": "executive_template.png",
        "template_file": "executive_template.html",
        "css_file": "executive_template.css"
    }
}

def create_default_templates():
    """Create default templates if they don't exist"""
    # Create Modern template
    modern_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ name }} | Resume</title>
    <style>
        /* Modern Template CSS */
        @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');
        
        body {
            font-family: 'Roboto', sans-serif;
            margin: 0;
            padding: 0;
            color: #333;
            background-color: #fff;
            font-size: 10pt;
        }
        
        .resume-container {
            display: flex;
            max-width: 8.5in;
            min-height: 11in;
            margin: 0 auto;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }
        
        .sidebar {
            background-color: #2c3e50;
            color: white;
            width: 30%;
            padding: 30px 20px;
        }
        
        .main-content {
            padding: 30px;
            width: 70%;
        }
        
        .profile-img {
            width: 120px;
            height: 120px;
            border-radius: 50%;
            margin: 0 auto 20px;
            display: block;
            background-color: #ddd;
            overflow: hidden;
        }
        
        h1 {
            color: #2c3e50;
            margin-top: 0;
            font-size: 24pt;
            font-weight: 700;
        }
        
        h2 {
            color: #3498db;
            border-bottom: 2px solid #3498db;
            padding-bottom: 5px;
            font-size: 14pt;
            margin-top: 20px;
        }
        
        .sidebar h2 {
            color: white;
            border-bottom: 2px solid white;
        }
        
        h3 {
            margin-bottom: 0;
            font-size: 12pt;
        }
        
        .company, .degree {
            color: #7f8c8d;
            font-weight: 500;
            margin-top: 0;
        }
        
        .date {
            font-style: italic;
            color: #95a5a6;
        }
        
        .contact-item {
            margin-bottom: 10px;
            display: flex;
            align-items: center;
        }
        
        .contact-icon {
            width: 16px;
            height: 16px;
            margin-right: 8px;
            filter: invert(1);
        }
        
        .skills-list {
            list-style-type: none;
            padding-left: 0;
        }
        
        .skills-list li {
            margin-bottom: 10px;
        }
        
        .skill-level {
            height: 6px;
            background-color: #ecf0f1;
            border-radius: 3px;
            margin-top: 5px;
        }
        
        .skill-level div {
            height: 100%;
            background-color: #3498db;
            border-radius: 3px;
        }
        
        .experience-item, .education-item, .project-item {
            margin-bottom: 20px;
        }
        
        .summary {
            margin-bottom: 30px;
            line-height: 1.5;
        }
    </style>
</head>
<body>
    <div class="resume-container">
        <div class="sidebar">
            {% if photo_url %}
            <div class="profile-img">
                <img src="{{ photo_url }}" alt="{{ name }}">
            </div>
            {% endif %}
            
            <div class="contact">
                <h2>CONTACT</h2>
                {% if email %}
                <div class="contact-item">
                    <span class="contact-icon">📧</span>
                    <span>{{ email }}</span>
                </div>
                {% endif %}
                
                {% if phone %}
                <div class="contact-item">
                    <span class="contact-icon">📱</span>
                    <span>{{ phone }}</span>
                </div>
                {% endif %}
                
                {% if location %}
                <div class="contact-item">
                    <span class="contact-icon">📍</span>
                    <span>{{ location }}</span>
                </div>
                {% endif %}
                
                {% if linkedin %}
                <div class="contact-item">
                    <span class="contact-icon">🔗</span>
                    <span>{{ linkedin }}</span>
                </div>
                {% endif %}
                
                {% if website %}
                <div class="contact-item">
                    <span class="contact-icon">🌐</span>
                    <span>{{ website }}</span>
                </div>
                {% endif %}
            </div>
            
            <div class="skills">
                <h2>SKILLS</h2>
                <ul class="skills-list">
                    {% for skill in skills %}
                    <li>
                        <span>{{ skill.name }}</span>
                        <div class="skill-level">
                            <div style="width: {{ skill.level }}%;"></div>
                        </div>
                    </li>
                    {% endfor %}
                </ul>
            </div>
            
            {% if languages %}
            <div class="languages">
                <h2>LANGUAGES</h2>
                <ul class="skills-list">
                    {% for language in languages %}
                    <li>
                        <span>{{ language.name }}</span>
                        <div class="skill-level">
                            <div style="width: {{ language.level }}%;"></div>
                        </div>
                    </li>
                    {% endfor %}
                </ul>
            </div>
            {% endif %}
            
            {% if certifications %}
            <div class="certifications">
                <h2>CERTIFICATIONS</h2>
                <ul>
                    {% for cert in certifications %}
                    <li>{{ cert }}</li>
                    {% endfor %}
                </ul>
            </div>
            {% endif %}
        </div>
        
        <div class="main-content">
            <h1>{{ name }}</h1>
            <p class="job-title">{{ job_title }}</p>
            
            {% if summary %}
            <div class="summary">
                <h2>SUMMARY</h2>
                <p>{{ summary }}</p>
            </div>
            {% endif %}
            
            <div class="experience">
                <h2>EXPERIENCE</h2>
                {% for job in experience %}
                <div class="experience-item">
                    <h3>{{ job.title }}</h3>
                    <p class="company">{{ job.company }}</p>
                    <p class="date">{{ job.date }}</p>
                    <ul>
                        {% for point in job.description %}
                        <li>{{ point }}</li>
                        {% endfor %}
                    </ul>
                </div>
                {% endfor %}
            </div>
            
            <div class="education">
                <h2>EDUCATION</h2>
                {% for edu in education %}
                <div class="education-item">
                    <h3>{{ edu.degree }}</h3>
                    <p class="degree">{{ edu.school }}</p>
                    <p class="date">{{ edu.date }}</p>
                    {% if edu.description %}
                    <p>{{ edu.description }}</p>
                    {% endif %}
                </div>
                {% endfor %}
            </div>
            
            {% if projects %}
            <div class="projects">
                <h2>PROJECTS</h2>
                {% for project in projects %}
                <div class="project-item">
                    <h3>{{ project.name }}</h3>
                    <p class="date">{{ project.date }}</p>
                    <p>{{ project.description }}</p>
                    {% if project.skills %}
                    <p><strong>Technologies:</strong> {{ project.skills }}</p>
                    {% endif %}
                </div>
                {% endfor %}
            </div>
            {% endif %}
        </div>
    </div>
</body>
</html>
"""

    professional_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ name }} | Professional Resume</title>
    <style>
        /* Professional Template CSS */
        @import url('https://fonts.googleapis.com/css2?family=Lato:wght@300;400;700&display=swap');
        
        body {
            font-family: 'Lato', sans-serif;
            margin: 0;
            padding: 0;
            color: #333;
            background-color: #fff;
            font-size: 11pt;
            line-height: 1.4;
        }
        
        .resume-container {
            max-width: 8.5in;
            margin: 0 auto;
            padding: 30px;
        }
        
        .header {
            text-align: center;
            margin-bottom: 20px;
            border-bottom: 1px solid #ccc;
            padding-bottom: 20px;
        }
        
        h1 {
            color: #2c3e50;
            margin: 0;
            font-size: 28pt;
            text-transform: uppercase;
            letter-spacing: 2px;
        }
        
        .job-title {
            font-size: 14pt;
            color: #7f8c8d;
            margin: 5px 0 15px;
        }
        
        .contact-info {
            display: flex;
            justify-content: center;
            flex-wrap: wrap;
        }
        
        .contact-item {
            margin: 0 15px;
            font-size: 10pt;
        }
        
        h2 {
            color: #2c3e50;
            border-bottom: 2px solid #2c3e50;
            padding-bottom: 5px;
            text-transform: uppercase;
            font-size: 14pt;
            margin-top: 25px;
            letter-spacing: 1px;
        }
        
        h3 {
            margin-bottom: 3px;
            font-size: 12pt;
        }
        
        .company, .degree {
            font-weight: 700;
            display: inline-block;
        }
        
        .date {
            float: right;
            font-style: italic;
            color: #7f8c8d;
        }
        
        .location {
            color: #7f8c8d;
            font-style: italic;
        }
        
        .experience-item, .education-item, .project-item {
            margin-bottom: 15px;
        }
        
        .experience-header, .education-header, .project-header {
            margin-bottom: 5px;
        }
        
        .summary {
            margin-bottom: 25px;
            text-align: justify;
        }
        
        .skills-container {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin-top: 10px;
        }
        
        .skill-tag {
            background-color: #f5f5f5;
            padding: 5px 10px;
            border-radius: 3px;
            font-size: 10pt;
        }
        
        ul {
            padding-left: 20px;
        }
        
        li {
            margin-bottom: 5px;
        }
    </style>
</head>
<body>
    <div class="resume-container">
        <div class="header">
            <h1>{{ name }}</h1>
            <p class="job-title">{{ job_title }}</p>
            
            <div class="contact-info">
                {% if email %}
                <div class="contact-item">
                    <strong>Email:</strong> {{ email }}
                </div>
                {% endif %}
                
                {% if phone %}
                <div class="contact-item">
                    <strong>Phone:</strong> {{ phone }}
                </div>
                {% endif %}
                
                {% if location %}
                <div class="contact-item">
                    <strong>Location:</strong> {{ location }}
                </div>
                {% endif %}
                
                {% if linkedin %}
                <div class="contact-item">
                    <strong>LinkedIn:</strong> {{ linkedin }}
                </div>
                {% endif %}
                
                {% if website %}
                <div class="contact-item">
                    <strong>Website:</strong> {{ website }}
                </div>
                {% endif %}
            </div>
        </div>
        
        {% if summary %}
        <div class="summary">
            <h2>Professional Summary</h2>
            <p>{{ summary }}</p>
        </div>
        {% endif %}
        
        <div class="experience">
            <h2>Professional Experience</h2>
            {% for job in experience %}
            <div class="experience-item">
                <div class="experience-header">
                    <h3>{{ job.title }}</h3>
                    <p>
                        <span class="company">{{ job.company }}</span>
                        <span class="date">{{ job.date }}</span>
                    </p>
                    {% if job.location %}
                    <p class="location">{{ job.location }}</p>
                    {% endif %}
                </div>
                <ul>
                    {% for point in job.description %}
                    <li>{{ point }}</li>
                    {% endfor %}
                </ul>
            </div>
            {% endfor %}
        </div>
        
        <div class="education">
            <h2>Education</h2>
            {% for edu in education %}
            <div class="education-item">
                <div class="education-header">
                    <h3>{{ edu.degree }}</h3>
                    <p>
                        <span class="degree">{{ edu.school }}</span>
                        <span class="date">{{ edu.date }}</span>
                    </p>
                </div>
                {% if edu.description %}
                <p>{{ edu.description }}</p>
                {% endif %}
            </div>
            {% endfor %}
        </div>
        
        <div class="skills">
            <h2>Skills</h2>
            <div class="skills-container">
                {% for skill in skills %}
                <div class="skill-tag">{{ skill.name }}</div>
                {% endfor %}
            </div>
        </div>
        
        {% if certifications %}
        <div class="certifications">
            <h2>Certifications</h2>
            <ul>
                {% for cert in certifications %}
                <li>{{ cert }}</li>
                {% endfor %}
            </ul>
        </div>
        {% endif %}
        
        {% if projects %}
        <div class="projects">
            <h2>Projects</h2>
            {% for project in projects %}
            <div class="project-item">
                <div class="project-header">
                    <h3>{{ project.name }}</h3>
                    {% if project.date %}
                    <p class="date">{{ project.date }}</p>
                    {% endif %}
                </div>
                <p>{{ project.description }}</p>
                {% if project.skills %}
                <p><strong>Technologies:</strong> {{ project.skills }}</p>
                {% endif %}
            </div>
            {% endfor %}
        </div>
        {% endif %}
    </div>
</body>
</html>
"""

    # Save templates
    with open(STATIC_TEMPLATE_DIR / "modern_template.html", "w") as f:
        f.write(modern_html)
        
    with open(STATIC_TEMPLATE_DIR / "professional_template.html", "w") as f:
        f.write(professional_html)
        
    # Create placeholder for other templates
    for template_id in ["creative", "technical", "executive"]:
        if not (STATIC_TEMPLATE_DIR / f"{template_id}_template.html").exists():
            with open(STATIC_TEMPLATE_DIR / f"{template_id}_template.html", "w") as f:
                f.write(f"<!DOCTYPE html><html><body><h1>{template_id.capitalize()} Template</h1><p>This is a placeholder. The actual template will be created soon.</p></body></html>")

def format_skills_for_template(skills_text: str) -> List[Dict[str, Union[str, int]]]:
    """
    Format skills text into a list of skill objects with name and level
    
    Args:
        skills_text: Text containing skills, typically comma separated
        
    Returns:
        List of skill objects with name and level (default 85% for all)
    """
    if not skills_text:
        return []
        
    # Split by commas and clean up
    skill_items = [s.strip() for s in skills_text.split(',')]
    
    # Filter out empty items
    skill_items = [s for s in skill_items if s]
    
    # Convert to objects with default 85% level
    return [{"name": skill, "level": 85} for skill in skill_items]

def structure_resume_data(tailored_sections: Dict[str, str]) -> Dict[str, Any]:
    """
    Structure resume data for template rendering
    
    Args:
        tailored_sections: Dictionary of resume sections with their tailored content
        
    Returns:
        Structured resume data for template rendering
    """
    # Default values
    resume_data = {
        "name": "John Doe",
        "job_title": "Professional Title",
        "email": "email@example.com",
        "phone": "(123) 456-7890",
        "location": "City, State",
        "linkedin": "linkedin.com/in/username",
        "website": "",
        "summary": "",
        "skills": [],
        "experience": [],
        "education": [],
        "projects": [],
        "certifications": [],
        "languages": []
    }
    
    # Extract contact info if available
    if "contact_info" in tailored_sections:
        contact_info = tailored_sections.get("contact_info", {})
        if isinstance(contact_info, dict):
            resume_data.update({
                "name": contact_info.get("name", resume_data["name"]),
                "email": contact_info.get("email", resume_data["email"]),
                "phone": contact_info.get("phone", resume_data["phone"]),
                "location": contact_info.get("location", resume_data["location"]),
                "linkedin": contact_info.get("linkedin", resume_data["linkedin"]),
                "website": contact_info.get("website", resume_data["website"]),
            })
    
    # Extract summary if available
    if "summary" in tailored_sections:
        resume_data["summary"] = tailored_sections.get("summary", "")
    
    # Format skills
    if "skills" in tailored_sections:
        skills_text = tailored_sections.get("skills", "")
        resume_data["skills"] = format_skills_for_template(skills_text)
    
    # Experience is more complex - we'd need to parse it
    # For now, just create a placeholder structure
    if "experience" in tailored_sections:
        experience_text = tailored_sections.get("experience", "")
        # Basic parsing - split by double newlines to separate jobs
        jobs = experience_text.split("\n\n")
        
        for job in jobs:
            if not job.strip():
                continue
                
            lines = job.strip().split("\n")
            if len(lines) < 2:
                continue
                
            # Try to extract title and company
            title = lines[0].strip()
            company = lines[1].strip() if len(lines) > 1 else ""
            date = "Present" if "present" in job.lower() else "2020 - 2023"  # Default date
            
            # Rest is description
            description = lines[2:] if len(lines) > 2 else []
            description = [line for line in description if line.strip()]
            
            if not description:
                description = ["Job description not available"]
            
            resume_data["experience"].append({
                "title": title,
                "company": company,
                "date": date,
                "description": description
            })
    
    # Education
    if "education" in tailored_sections:
        education_text = tailored_sections.get("education", "")
        # Basic parsing - split by double newlines to separate education entries
        edu_entries = education_text.split("\n\n")
        
        for edu in edu_entries:
            if not edu.strip():
                continue
                
            lines = edu.strip().split("\n")
            if not lines:
                continue
                
            # Try to extract degree and school
            degree = lines[0].strip()
            school = lines[1].strip() if len(lines) > 1 else ""
            date = "2018 - 2022"  # Default date
            
            # Rest is description
            description = "\n".join(lines[2:]) if len(lines) > 2 else ""
            
            resume_data["education"].append({
                "degree": degree,
                "school": school,
                "date": date,
                "description": description
            })
    
    # Projects
    if "projects" in tailored_sections:
        projects_text = tailored_sections.get("projects", "")
        # Basic parsing - split by double newlines to separate projects
        project_entries = projects_text.split("\n\n")
        
        for project in project_entries:
            if not project.strip():
                continue
                
            lines = project.strip().split("\n")
            if not lines:
                continue
                
            # Try to extract project name
            name = lines[0].strip()
            
            # Rest is description
            description = "\n".join(lines[1:]) if len(lines) > 1 else ""
            
            resume_data["projects"].append({
                "name": name,
                "date": "2023",  # Default date
                "description": description,
                "skills": "Relevant technologies"
            })
    
    # Certifications
    if "certifications" in tailored_sections:
        cert_text = tailored_sections.get("certifications", "")
        # Split by newlines and/or commas
        cert_items = []
        for line in cert_text.split("\n"):
            cert_items.extend([c.strip() for c in line.split(",")])
        
        # Filter out empty items
        cert_items = [c for c in cert_items if c]
        resume_data["certifications"] = cert_items
    
    return resume_data

def generate_resume_pdf(template_id: str, tailored_sections: Dict[str, str]) -> Optional[bytes]:
    """
    Generate a PDF resume from a template and tailored content
    
    Args:
        template_id: ID of the template to use
        tailored_sections: Dictionary of resume sections with their tailored content
        
    Returns:
        PDF content as bytes, or None if generation failed
    """
    if not WEASYPRINT_AVAILABLE:
        st.error("WeasyPrint is not installed. PDF generation is not available.")
        return None
    
    # Ensure default templates exist
    create_default_templates()
    
    # Get template info
    template_info = RESUME_TEMPLATES.get(template_id)
    if not template_info:
        st.error(f"Template '{template_id}' not found.")
        return None
    
    template_file = template_info["template_file"]
    
    # Check if template file exists
    template_path = STATIC_TEMPLATE_DIR / template_file
    if not template_path.exists():
        st.error(f"Template file '{template_file}' not found.")
        return None
    
    # Structure data for template
    resume_data = structure_resume_data(tailored_sections)
    
    # Load template
    try:
        template = template_env.get_template(template_file)
    except Exception as e:
        st.error(f"Error loading template: {str(e)}")
        return None
    
    # Render template
    try:
        html_content = template.render(**resume_data)
    except Exception as e:
        st.error(f"Error rendering template: {str(e)}")
        return None
    
    # Generate PDF
    try:
        with tempfile.NamedTemporaryFile(suffix='.html', delete=False) as tmp_html:
            tmp_html.write(html_content.encode('utf-8'))
            tmp_html_path = tmp_html.name
        
        # Generate PDF using WeasyPrint
        pdf = HTML(filename=tmp_html_path).write_pdf()
        
        # Clean up temp file
        os.unlink(tmp_html_path)
        
        return pdf
    except Exception as e:
        st.error(f"Error generating PDF: {str(e)}")
        return None

def get_pdf_download_link(pdf_bytes: bytes, filename: str = "resume.pdf") -> str:
    """
    Generate a download link for a PDF
    
    Args:
        pdf_bytes: PDF content as bytes
        filename: Name of the file for download
        
    Returns:
        HTML link to download the PDF
    """
    b64 = base64.b64encode(pdf_bytes).decode()
    href = f'<a href="data:application/pdf;base64,{b64}" download="{filename}" style="display: inline-block; padding: 0.5rem 1rem; background-color: #4361EE; color: white; text-decoration: none; border-radius: 0.375rem; font-weight: 600; margin-top: 1rem;">Download Resume PDF</a>'
    return href

def render_template_selection(tailored_sections: Dict[str, str], selected_template_id: str = "modern") -> str:
    """
    Render the template selection UI and generate PDF
    
    Args:
        tailored_sections: Dictionary of resume sections with their tailored content
        selected_template_id: ID of the currently selected template
        
    Returns:
        Selected template ID
    """
    st.markdown("<h3 style='margin-top: 1.5rem;'>Select Resume Template</h3>", unsafe_allow_html=True)
    
    # Create columns for template selection
    cols = st.columns(3)
    
    # Render template options
    templates_list = list(RESUME_TEMPLATES.items())
    for i, (template_id, template_info) in enumerate(templates_list):
        col_idx = i % 3
        with cols[col_idx]:
            card_style = "border: 2px solid #4361EE;" if template_id == selected_template_id else "border: 1px solid #e5e7eb;"
            st.markdown(f"""
            <div style="{card_style} border-radius: 8px; padding: 1rem; margin-bottom: 1rem; background-color: white;">
                <h4 style="margin-top: 0; margin-bottom: 0.5rem; color: #1e293b;">{template_info['name']}</h4>
                <p style="color: #64748b; font-size: 0.875rem; margin-bottom: 1rem;">{template_info['description']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Button to select this template
            if st.button(f"Select {template_info['name']}", key=f"select_template_{template_id}"):
                selected_template_id = template_id
                st.session_state.job_selected_template = template_id
                st.rerun()
    
    # Generate PDF preview
    st.markdown("<h3 style='margin-top: 1.5rem;'>Preview and Download</h3>", unsafe_allow_html=True)
    
    # Show a loading spinner while generating the PDF
    with st.spinner("Generating your resume PDF..."):
        pdf_bytes = generate_resume_pdf(selected_template_id, tailored_sections)
    
    if pdf_bytes:
        # Display download button
        st.markdown(get_pdf_download_link(pdf_bytes), unsafe_allow_html=True)
        
        # Show an iframe preview
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_pdf:
            tmp_pdf.write(pdf_bytes)
            tmp_pdf_path = tmp_pdf.name
        
        try:
            # Create a data URL for the PDF
            b64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
            pdf_display = f'<iframe src="data:application/pdf;base64,{b64_pdf}" width="100%" height="600" style="border: 1px solid #ccc; border-radius: 5px;"></iframe>'
            st.markdown(pdf_display, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Error displaying PDF preview: {str(e)}")
        
        # Clean up temp file
        os.unlink(tmp_pdf_path)
    else:
        st.error("Failed to generate PDF. Please try a different template or check your content.")
    
    return selected_template_id 