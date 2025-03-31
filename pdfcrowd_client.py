import pdfcrowd
import tempfile
import os
import streamlit as st
from utils.api_config import API_CONFIG

class PDFCrowdClient:
    def __init__(self):
        self.config = API_CONFIG["pdfcrowd"]
        self.username = self.config["username"]
        self.api_key = self.config["api_key"]
        self.initialized = self.username is not None and self.api_key is not None
        self.client = None
        self.initialize_client()
        
    def initialize_client(self):
        """Initialize PDFCrowd client with API credentials"""
        if not self.initialized:
            return
            
        try:
            self.client = pdfcrowd.HtmlToPdfClient(self.username, self.api_key)
            
            # Set default options
            self.client.setPageWidth("8.5in")
            self.client.setPageHeight("11in")
            self.client.setMarginTop("0.5in")
            self.client.setMarginBottom("0.5in")
            self.client.setMarginLeft("0.75in")
            self.client.setMarginRight("0.75in")
            
        except Exception as e:
            st.warning(f"PDFCrowd initialization error: {str(e)}")
    
    def html_to_pdf(self, html_content, output_file=None, options=None):
        """
        Convert HTML content to PDF
        
        Args:
            html_content: HTML content to convert
            output_file: File path to save PDF (if None, temp file is created)
            options: Dictionary of PDFCrowd options
            
        Returns:
            tuple: (success, file_path or error message)
        """
        if not self.initialized or self.client is None:
            return (False, "PDFCrowd client not initialized")
            
        # Create a temp file if output_file is not specified
        if output_file is None:
            # Create temp file
            fd, output_file = tempfile.mkstemp(suffix=".pdf")
            os.close(fd)
        
        try:
            # Apply custom options if provided
            if options:
                for key, value in options.items():
                    # Convert option names from snake_case to camelCase method names
                    option_parts = key.split('_')
                    method_name = 'set' + ''.join(p.capitalize() for p in option_parts)
                    
                    # Call the corresponding method if it exists
                    if hasattr(self.client, method_name):
                        getattr(self.client, method_name)(value)
            
            # Convert HTML to PDF
            self.client.convertStringToFile(html_content, output_file)
            
            return (True, output_file)
            
        except pdfcrowd.Error as e:
            st.error(f"PDFCrowd conversion error: {str(e)}")
            return (False, str(e))
    
    def generate_resume_pdf(self, resume_sections, template_name="modern"):
        """
        Generate a professional resume PDF
        
        Args:
            resume_sections: Dictionary of resume sections
            template_name: Name of the template to use
            
        Returns:
            tuple: (success, file_path or error message)
        """
        # Apply the template to create HTML content
        html_content = self._apply_template(resume_sections, template_name)
        
        # Set template-specific options
        options = self._get_template_options(template_name)
        
        # Convert to PDF
        return self.html_to_pdf(html_content, options=options)
    
    def _get_template_options(self, template_name):
        """
        Get PDFCrowd options for a specific template
        
        Args:
            template_name: Name of the template
            
        Returns:
            dict: PDFCrowd options
        """
        # Default options
        options = {}
        
        # Template-specific options
        if template_name == "modern":
            options = {
                "page_width": "8.5in",
                "page_height": "11in",
                "margin_top": "0.5in",
                "margin_bottom": "0.5in",
                "margin_left": "0.75in",
                "margin_right": "0.75in",
                "header_html": "<div></div>",  # Empty header
                "footer_html": "<div style='text-align: center; font-size: 8pt; color: #666;'>Page <span class='pdfcrowd-page-number'></span> of <span class='pdfcrowd-page-count'></span></div>"
            }
        elif template_name == "technical":
            options = {
                "page_width": "8.5in",
                "page_height": "11in",
                "margin_top": "0.5in",
                "margin_bottom": "0.5in",
                "margin_left": "0.75in",
                "margin_right": "0.75in",
                "header_html": "<div></div>",  # Empty header
                "footer_html": "<div style='text-align: center; font-size: 8pt; color: #666;'>Page <span class='pdfcrowd-page-number'></span> of <span class='pdfcrowd-page-count'></span></div>"
            }
        elif template_name == "minimalist":
            options = {
                "page_width": "8.5in",
                "page_height": "11in",
                "margin_top": "0.5in",
                "margin_bottom": "0.5in",
                "margin_left": "0.75in",
                "margin_right": "0.75in",
                "header_html": "<div></div>",  # Empty header
                "footer_html": "<div style='text-align: center; font-size: 8pt; color: #666;'>Page <span class='pdfcrowd-page-number'></span> of <span class='pdfcrowd-page-count'></span></div>"
            }
        
        return options
    
    def _apply_template(self, resume_sections, template_name):
        """
        Apply a template to resume sections
        
        Args:
            resume_sections: Dictionary of resume sections
            template_name: Name of the template to use
            
        Returns:
            str: HTML content
        """
        # Base HTML structure
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Professional Resume</title>
            <style>
                {css}
            </style>
        </head>
        <body>
            <div class="resume-container">
                {content}
            </div>
        </body>
        </html>
        """
        
        # Get template-specific CSS
        css = self._get_template_css(template_name)
        
        # Generate the content based on resume sections
        content = ""
        
        # Header section (Contact + Summary)
        header = ""
        if "Contact" in resume_sections and resume_sections["Contact"] != "Missing":
            contact_html = f"""
            <div class="contact-info">
                {resume_sections["Contact"]}
            </div>
            """
            header += contact_html
        
        if "Summary" in resume_sections and resume_sections["Summary"] != "Missing":
            summary_html = f"""
            <div class="summary-section">
                <h2>Professional Summary</h2>
                <div class="section-content">
                    {resume_sections["Summary"]}
                </div>
            </div>
            """
            header += summary_html
        
        content += f"<div class='resume-header'>{header}</div>"
        
        # Main content sections
        main_content = ""
        
        # Education
        if "Education" in resume_sections and resume_sections["Education"] != "Missing":
            education_html = f"""
            <div class="resume-section">
                <h2>Education</h2>
                <div class="section-content">
                    {resume_sections["Education"]}
                </div>
            </div>
            """
            main_content += education_html
        
        # Work Experience
        if "Work Experience" in resume_sections and resume_sections["Work Experience"] != "Missing":
            experience_html = f"""
            <div class="resume-section">
                <h2>Work Experience</h2>
                <div class="section-content">
                    {resume_sections["Work Experience"]}
                </div>
            </div>
            """
            main_content += experience_html
        
        # Skills
        if "Skills" in resume_sections and resume_sections["Skills"] != "Missing":
            skills_html = f"""
            <div class="resume-section">
                <h2>Skills</h2>
                <div class="section-content">
                    {resume_sections["Skills"]}
                </div>
            </div>
            """
            main_content += skills_html
        
        # Projects
        if "Projects" in resume_sections and resume_sections["Projects"] != "Missing":
            projects_html = f"""
            <div class="resume-section">
                <h2>Projects</h2>
                <div class="section-content">
                    {resume_sections["Projects"]}
                </div>
            </div>
            """
            main_content += projects_html
        
        # Certifications
        if "Certifications" in resume_sections and resume_sections["Certifications"] != "Missing":
            certifications_html = f"""
            <div class="resume-section">
                <h2>Certifications</h2>
                <div class="section-content">
                    {resume_sections["Certifications"]}
                </div>
            </div>
            """
            main_content += certifications_html
        
        # Languages
        if "Languages" in resume_sections and resume_sections["Languages"] != "Missing":
            languages_html = f"""
            <div class="resume-section">
                <h2>Languages</h2>
                <div class="section-content">
                    {resume_sections["Languages"]}
                </div>
            </div>
            """
            main_content += languages_html
        
        # Add other sections
        for section_name, content_text in resume_sections.items():
            if content_text != "Missing" and section_name not in [
                "Contact", "Summary", "Education", "Work Experience", 
                "Skills", "Projects", "Certifications", "Languages"
            ]:
                section_html = f"""
                <div class="resume-section">
                    <h2>{section_name}</h2>
                    <div class="section-content">
                        {content_text}
                    </div>
                </div>
                """
                main_content += section_html
        
        content += f"<div class='resume-body'>{main_content}</div>"
        
        # Fill in the HTML template
        html = html.format(css=css, content=content)
        
        return html
    
    def _get_template_css(self, template_name):
        """
        Get CSS for a specific template
        
        Args:
            template_name: Name of the template
            
        Returns:
            str: CSS styles
        """
        # Base CSS
        base_css = """
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: Arial, sans-serif;
                color: #333;
                line-height: 1.5;
            }
            
            .resume-container {
                width: 100%;
                max-width: 8.5in;
                margin: 0 auto;
            }
            
            h1, h2, h3 {
                margin-bottom: 0.5rem;
            }
            
            .resume-section {
                margin-bottom: 1.25rem;
            }
            
            .section-content {
                margin-top: 0.3rem;
            }
        """
        
        # Template-specific CSS
        if template_name == "modern":
            template_css = """
                body {
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    color: #333;
                }
                
                .resume-header {
                    padding-bottom: 1.5rem;
                    margin-bottom: 1.5rem;
                    border-bottom: 2px solid #4361EE;
                }
                
                .contact-info {
                    font-size: 0.9rem;
                    color: #555;
                }
                
                h2 {
                    color: #4361EE;
                    font-size: 1.3rem;
                    border-bottom: 1px solid #ddd;
                    padding-bottom: 0.3rem;
                }
                
                .summary-section {
                    margin-top: 1rem;
                }
            """
        elif template_name == "technical":
            template_css = """
                body {
                    font-family: 'Courier New', monospace;
                    color: #2c3e50;
                }
                
                .resume-header {
                    padding-bottom: 1.5rem;
                    margin-bottom: 1.5rem;
                    border-bottom: 2px solid #3498db;
                }
                
                .contact-info {
                    font-size: 0.9rem;
                    color: #555;
                }
                
                h2 {
                    color: #3498db;
                    font-size: 1.3rem;
                    border-bottom: 1px solid #ddd;
                    padding-bottom: 0.3rem;
                }
                
                .summary-section {
                    margin-top: 1rem;
                }
                
                /* Technical template has a side column for skills */
                @media print {
                    .resume-body {
                        display: grid;
                        grid-template-columns: 70% 30%;
                        grid-gap: 1.5rem;
                    }
                    
                    .skills-section {
                        grid-column: 2;
                        grid-row: 1 / span 3;
                        background-color: #f8f9fa;
                        padding: 1rem;
                        border-radius: 5px;
                    }
                }
            """
        elif template_name == "minimalist":
            template_css = """
                body {
                    font-family: Arial, sans-serif;
                    color: #555;
                    line-height: 1.8;
                }
                
                .resume-header {
                    padding-bottom: 1rem;
                    margin-bottom: 1rem;
                    text-align: center;
                }
                
                .contact-info {
                    font-size: 0.9rem;
                    text-align: center;
                }
                
                h2 {
                    color: #333;
                    font-size: 1.2rem;
                    text-transform: uppercase;
                    letter-spacing: 1px;
                    margin-top: 1.5rem;
                }
                
                .summary-section {
                    margin-top: 1rem;
                    text-align: center;
                    font-style: italic;
                }
            """
        else:
            # Default CSS
            template_css = ""
        
        return base_css + template_css

# Initialize PDFCrowd client
pdfcrowd_client = PDFCrowdClient() 