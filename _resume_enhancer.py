"""
Resume Enhancer Page - Helps users enhance their resumes with AI
"""

import streamlit as st
import os
import sys
import time
from datetime import datetime
import tempfile
import traceback
from pathlib import Path
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add parent directory to path for module imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import required modules with fallbacks
try:
    # Import core modules
    from pages._init import render_step_indicator, render_section_title, render_info_box, initialize_session
    
    # Import resume processing utilities with fallbacks
    try:
        from utils.resume_processor import (
            extract_text_from_pdf,
            extract_text_advanced,
            extract_structured_data_advanced,
            generate_confidence_scores,
            find_missing_sections,
            check_grammar
        )
        resume_processor_available = True
    except ImportError as e:
        logger.error(f"Error importing resume_processor: {str(e)}")
        resume_processor_available = False
    
    # Import highlight utilities with fallbacks
    try:
        from utils.highlight_utils import (
            highlight_keywords, 
            highlight_with_feedback, 
            extract_keywords_from_text, 
            find_improvement_suggestions
        )
        highlight_utils_available = True
    except ImportError as e:
        logger.error(f"Error importing highlight_utils: {str(e)}")
        highlight_utils_available = False
    
    # Import Gemini feedback utilities with fallbacks
    try:
        from utils.gemini_feedback import (
            generate_gemini_feedback_for_resume, 
            display_gemini_feedback, 
            apply_gemini_quick_fix
        )
        gemini_feedback_available = True
    except ImportError as e:
        logger.error(f"Error importing gemini_feedback: {str(e)}")
        gemini_feedback_available = False
        
except ImportError as e:
    logger.error(f"Critical import error: {str(e)}")
    # We'll handle this in the main function

# Define the steps for the resume enhancer
steps = [
    ("Upload Resume", "📤"),
    ("Analyze Content", "🔍"),
    ("Enhance Resume", "✨"),
    ("Download Resume", "📄")
]

def initialize_resume_state():
    """Initialize session state variables for the resume enhancer"""
    # Initialize common session variables
    try:
        initialize_session()
    except:
        # Fallback if _init module is not available
        pass
    
    # Resume enhancer specific state
    if 'resume_text' not in st.session_state:
        st.session_state.resume_text = ""
    
    if 'resume_sections' not in st.session_state:
        st.session_state.resume_sections = {}
    
    if 'resume_enhancer_step' not in st.session_state:
        st.session_state.resume_enhancer_step = 0  # Start at the upload step
    
    if 'enhanced_sections' not in st.session_state:
        st.session_state.enhanced_sections = {}

def set_step(step):
    """Set the current step in the resume enhancer workflow"""
    st.session_state.resume_enhancer_step = step
    st.rerun()

def show_upload_step():
    """Show the resume upload step"""
    render_section_title("Upload Resume", "Step 1: Upload your resume to get started")
    
    # Instructions
    st.markdown("""
    Upload your resume (PDF format) to begin the analysis. We'll extract the content and 
    provide suggestions to improve each section.
    """)
    
    # File uploader
    uploaded_file = st.file_uploader(
        "Upload your resume (PDF format)", 
        type=["pdf"],
        help="PDF files are recommended for best results."
    )
    
    if uploaded_file:
        with st.spinner("Processing your resume..."):
            # Create progress indicators
            progress_placeholder = st.empty()
            progress_bar = st.progress(0)
            
            # Extract text from the PDF
            temp_dir = tempfile.mkdtemp()
            temp_file_path = os.path.join(temp_dir, uploaded_file.name)
            
            with open(temp_file_path, "wb") as f:
                f.write(uploaded_file.getvalue())
            
            try:
                # Update progress
                progress_placeholder.text("Extracting text from PDF...")
                progress_bar.progress(25)
                
                # Extract text from PDF using appropriate function
                if resume_processor_available:
                    resume_text, metadata = extract_text_advanced(temp_file_path)
                    if not resume_text:
                        resume_text = extract_text_from_pdf(temp_file_path)
                else:
                    # Basic fallback if module not available
                    import PyPDF2
                    with open(temp_file_path, 'rb') as file:
                        reader = PyPDF2.PdfReader(file)
                        resume_text = ""
                        for page in reader.pages:
                            resume_text += page.extract_text() + "\n"
                
                # Save to session state
                st.session_state.resume_text = resume_text
                st.session_state.resume_file_path = temp_file_path
                
                # Update progress
                progress_placeholder.text("Analyzing resume structure...")
                progress_bar.progress(50)
                
                # Extract structured data
                if resume_processor_available:
                    resume_sections = extract_structured_data_advanced(resume_text)
                    st.session_state.resume_sections = resume_sections
                    
                    # Get additional analysis
                    confidence_scores = generate_confidence_scores(resume_sections)
                    missing_sections = find_missing_sections(resume_sections)
                    grammar_issues = check_grammar(resume_text)
                    
                    st.session_state.confidence_scores = confidence_scores
                    st.session_state.missing_sections = missing_sections
                    st.session_state.grammar_issues = grammar_issues
                    
                    # Get keywords and suggestions if available
                    if highlight_utils_available:
                        keywords = extract_keywords_from_text(resume_text)
                        suggestions = find_improvement_suggestions(resume_text)
                        
                        st.session_state.resume_keywords = keywords
                        st.session_state.improvement_suggestions = suggestions
                    
                    # Try to get Gemini feedback if available
                    if gemini_feedback_available:
                        try:
                            gemini_feedback = generate_gemini_feedback_for_resume(resume_text, resume_sections)
                            if gemini_feedback:
                                st.session_state.gemini_feedback = gemini_feedback
                        except Exception as e:
                            logger.error(f"Error getting Gemini feedback: {str(e)}")
                
                # Update progress
                progress_placeholder.text("Analysis complete!")
                progress_bar.progress(100)
                
                # Advance to next step
                set_step(1)
                
            except Exception as e:
                st.error(f"Error processing resume: {str(e)}")
                logger.error(f"Error processing resume: {traceback.format_exc()}")
    
    # Demo option
    if st.button("Try Demo Resume"):
        # Load demo resume
        demo_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "sample_resume.pdf")
        if os.path.exists(demo_path):
            with st.spinner("Loading demo resume..."):
                st.session_state.resume_file_path = demo_path
                
                # Extract text and data
                if resume_processor_available:
                    resume_text, _ = extract_text_advanced(demo_path)
                    resume_sections = extract_structured_data_advanced(resume_text)
                    
                    # Store in session state
                    st.session_state.resume_text = resume_text
                    st.session_state.resume_sections = resume_sections
                    
                    # Get additional analysis
                    st.session_state.confidence_scores = generate_confidence_scores(resume_sections)
                    st.session_state.missing_sections = find_missing_sections(resume_sections)
                    st.session_state.grammar_issues = check_grammar(resume_text)
                    
                    # Get keywords and suggestions if available
                    if highlight_utils_available:
                        st.session_state.resume_keywords = extract_keywords_from_text(resume_text)
                        st.session_state.improvement_suggestions = find_improvement_suggestions(resume_text)
                    
                    # Advance to next step
                    set_step(1)
                else:
                    st.error("Demo mode requires the resume processor module.")
        else:
            st.error("Demo resume not found. Please upload your own resume.")

def show_analyze_step():
    """Show the resume analysis step"""
    render_section_title("Resume Analysis", "Step 2: Review our analysis of your resume")
    
    if not st.session_state.resume_sections:
        st.warning("No resume data to analyze. Please go back to Step 1 and upload your resume.")
        if st.button("← Go Back to Upload"):
            set_step(0)
        return
    
    # Display resume content
    with st.expander("Resume Content", expanded=True):
        if st.session_state.resume_text:
            st.markdown("### Your Resume Text")
            
            # Show highlighted text with feedback if available
            if highlight_utils_available and "resume_keywords" in st.session_state and "improvement_suggestions" in st.session_state:
                highlighted_text = highlight_with_feedback(
                    st.session_state.resume_text,
                    st.session_state.resume_keywords,
                    st.session_state.improvement_suggestions
                )
                st.markdown(highlighted_text, unsafe_allow_html=True)
            else:
                # Simple fallback display
                st.text_area("Resume Text", st.session_state.resume_text, height=300, disabled=True)
    
    # Display section quality scores if available
    if "confidence_scores" in st.session_state and st.session_state.confidence_scores:
        with st.expander("Section Quality", expanded=True):
            st.markdown("### Section Quality Scores")
            
            # Display scores as a simple table
            for section, score in st.session_state.confidence_scores.items():
                st.markdown(f"**{section}**: {score}")
                
                # Simple visual indicator
                st.progress(min(score/100, 1.0))
    
    # Display missing sections if available
    if "missing_sections" in st.session_state and st.session_state.missing_sections:
        with st.expander("Missing Sections", expanded=True):
            st.markdown("### Missing or Weak Sections")
            for section in st.session_state.missing_sections:
                render_info_box(f"Missing: **{section}**", "warning")
    
    # Display grammar issues if available
    if "grammar_issues" in st.session_state and st.session_state.grammar_issues:
        with st.expander("Grammar & Style", expanded=True):
            st.markdown("### Grammar and Style Issues")
            
            if isinstance(st.session_state.grammar_issues, dict):
                # The structured dictionary format
                for category, issues in st.session_state.grammar_issues.items():
                    if issues:
                        st.markdown(f"#### {category}")
                        for issue in issues:
                            render_info_box(issue, "warning")
            else:
                # Legacy format (list of issues)
                for issue in st.session_state.grammar_issues:
                    render_info_box(issue, "warning")
    
    # Display Gemini feedback if available
    if gemini_feedback_available and "gemini_feedback" in st.session_state and st.session_state.gemini_feedback:
        with st.expander("AI Assistant Feedback", expanded=True):
            display_gemini_feedback(st.session_state.gemini_feedback)
    
    # Navigation buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Back to Upload"):
            set_step(0)
    with col2:
        if st.button("Next: Enhance Resume →"):
            set_step(2)

def show_enhance_step():
    """Show the enhance resume step"""
    render_section_title("Enhance Resume", "Step 3: Enhance your resume with our suggestions")
    
    # Check if we have resume sections to enhance
    if not st.session_state.resume_sections:
        st.warning("No resume data to enhance. Please go back to Step 1 and upload your resume.")
        if st.button("← Go Back to Upload"):
            set_step(0)
        return
    
    # Get suggested improvements from Gemini if available
    if gemini_feedback_available and "gemini_feedback" in st.session_state and "suggestions" in st.session_state.gemini_feedback:
        with st.expander("AI Assistant Suggestions", expanded=True):
            st.markdown("### AI-Powered Improvement Suggestions")
            
            # Process each suggestion category
            for category, suggestions in st.session_state.gemini_feedback["suggestions"].items():
                if suggestions:
                    st.markdown(f"#### {category}")
                    for i, suggestion in enumerate(suggestions):
                        col1, col2 = st.columns([4, 1])
                        with col1:
                            st.markdown(f"{suggestion}")
                        with col2:
                            if st.button("Apply", key=f"apply_{category}_{i}"):
                                # Apply the quick fix
                                if apply_gemini_quick_fix(suggestion, st.session_state.resume_sections):
                                    st.success("Applied suggestion!")
                                    st.rerun()
    
    # Initialize enhanced_sections with original sections if empty
    if not st.session_state.enhanced_sections:
        st.session_state.enhanced_sections = {}
        for section, content in st.session_state.resume_sections.items():
            if isinstance(content, dict) and "content" in content:
                st.session_state.enhanced_sections[section] = content["content"]
            elif isinstance(content, str):
                st.session_state.enhanced_sections[section] = content
            else:
                st.session_state.enhanced_sections[section] = str(content)
    
    # Show section editors for each resume section
    sections_to_edit = st.session_state.resume_sections.keys()
    
    for section in sections_to_edit:
        with st.expander(f"{section}", expanded=False):
            # Get section content
            if isinstance(st.session_state.resume_sections[section], dict) and "content" in st.session_state.resume_sections[section]:
                original_content = st.session_state.resume_sections[section]["content"]
            elif isinstance(st.session_state.resume_sections[section], str):
                original_content = st.session_state.resume_sections[section]
            else:
                original_content = str(st.session_state.resume_sections[section])
            
            if section not in st.session_state.enhanced_sections:
                st.session_state.enhanced_sections[section] = original_content
            
            # Create editor - using standard text area
            st.session_state.enhanced_sections[section] = st.text_area(
                "Edit Content", 
                value=st.session_state.enhanced_sections[section],
                height=300,
                key=f"textarea_{section}"
            )
            
            # Save indicator
            if st.session_state.enhanced_sections[section] != original_content:
                st.success(f"Changes to {section} auto-saved!")
    
    # Provide template selection
    st.markdown("### Select Resume Template")
    template_options = {
        "professional": "Professional (Default)",
        "modern": "Modern",
        "simple": "Simple"
    }
    selected_template = st.selectbox(
        "Choose a template for your enhanced resume",
        options=list(template_options.keys()),
        format_func=lambda x: template_options[x],
        index=0
    )
    
    if "selected_template" not in st.session_state or selected_template != st.session_state.selected_template:
        st.session_state.selected_template = selected_template
        st.success(f"Template set to {template_options[selected_template]}")
    
    # Navigation buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Back to Analysis"):
            set_step(1)
    with col2:
        if st.button("Next: Download Resume →"):
            set_step(3)

def show_download_step():
    """Show the download enhanced resume step"""
    render_section_title("Download Resume", "Step 4: Download your enhanced resume")
    
    # Check if we have enhanced sections
    if not st.session_state.enhanced_sections:
        st.warning("No enhanced resume data available. Please go back and enhance your resume.")
        if st.button("← Go Back to Enhance"):
            set_step(2)
        return
    
    # Show before/after comparison
    with st.expander("Before and After Comparison", expanded=True):
        before_col, after_col = st.columns(2)
        
        with before_col:
            st.markdown("### Original Resume")
            if st.session_state.resume_text:
                st.text_area("Original Text", st.session_state.resume_text, height=400, disabled=True)
        
        with after_col:
            st.markdown("### Enhanced Resume")
            # Combine enhanced sections
            enhanced_text = ""
            for section, content in st.session_state.enhanced_sections.items():
                enhanced_text += f"\n\n{section.upper()}\n\n{content}"
            
            st.text_area("Enhanced Text", enhanced_text, height=400, disabled=True)
    
    # Download options
    st.markdown("### Download your enhanced resume")
    
    # Create download options
    download_formats = ["PDF", "TXT"]
    selected_format = st.selectbox("Select download format", download_formats)
    
    # Create a temp directory for generated files
    output_dir = tempfile.mkdtemp()
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if st.button("Generate Resume"):
        with st.spinner(f"Generating {selected_format} file..."):
            try:
                # Get combined text from enhanced sections
                enhanced_text = ""
                for section, content in st.session_state.enhanced_sections.items():
                    enhanced_text += f"\n\n{section.upper()}\n\n{content}"
                
                # Generate the appropriate file based on the selected format
                if selected_format == "PDF":
                    # Basic PDF generation
                    output_path = os.path.join(output_dir, f"enhanced_resume_{current_time}.pdf")
                    
                    try:
                        # Try to use reportlab for PDF generation
                        from reportlab.lib.pagesizes import letter
                        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
                        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
                        
                        doc = SimpleDocTemplate(output_path, pagesize=letter)
                        styles = getSampleStyleSheet()
                        story = []
                        
                        # Add content
                        for section, content in st.session_state.enhanced_sections.items():
                            # Add section heading
                            story.append(Paragraph(section.upper(), styles['Heading1']))
                            story.append(Spacer(1, 12))
                            
                            # Add section content
                            for paragraph in content.split('\n\n'):
                                if paragraph.strip():
                                    story.append(Paragraph(paragraph, styles['Normal']))
                                    story.append(Spacer(1, 12))
                        
                        doc.build(story)
                    except ImportError:
                        # Fallback to a simpler PDF generator if reportlab is not available
                        try:
                            from fpdf import FPDF
                            pdf = FPDF()
                            pdf.add_page()
                            pdf.set_font("Arial", size=12)
                            
                            # Add content
                            for line in enhanced_text.split('\n'):
                                pdf.cell(200, 10, txt=line[:80], ln=True)  # Limiting line length
                            
                            pdf.output(output_path)
                        except ImportError:
                            st.error("PDF generation libraries not available. Please download as TXT instead.")
                            return
                else:  # TXT
                    # Generate TXT file
                    output_path = os.path.join(output_dir, f"enhanced_resume_{current_time}.txt")
                    with open(output_path, 'w') as f:
                        f.write(enhanced_text)
                
                # Provide download link
                with open(output_path, "rb") as file:
                    file_bytes = file.read()
                    st.download_button(
                        label=f"Download {selected_format} File",
                        data=file_bytes,
                        file_name=os.path.basename(output_path),
                        mime="application/octet-stream"
                    )
                
                st.success(f"Resume generated successfully! Click the download button above.")
            except Exception as e:
                st.error(f"Error generating resume: {str(e)}")
                logger.error(f"Error generating resume: {traceback.format_exc()}")
    
    # Navigation buttons
    if st.button("← Back to Enhance"):
        set_step(2)
    
    # Provide option to start over
    st.markdown("---")
    if st.button("Start Over with a New Resume"):
        # Reset session state
        for key in ['resume_text', 'resume_sections', 'enhanced_sections', 'resume_file_path']:
            if key in st.session_state:
                del st.session_state[key]
        
        set_step(0)

def main():
    """Main entry point for resume enhancer page"""
    try:
        # Initialize variables if needed
        initialize_resume_state()
        
        # Page title and description
        st.title("Resume Enhancer")
        
        # Show step indicator
        render_step_indicator(steps, st.session_state.resume_enhancer_step)
        
        # Display current step based on session state
        if st.session_state.resume_enhancer_step == 0:
            show_upload_step()
        elif st.session_state.resume_enhancer_step == 1:
            show_analyze_step()
        elif st.session_state.resume_enhancer_step == 2:
            show_enhance_step()
        elif st.session_state.resume_enhancer_step == 3:
            show_download_step()
            
    except Exception as e:
        st.error(f"An error occurred in the Resume Enhancer: {str(e)}")
        logger.error(f"Error in Resume Enhancer: {traceback.format_exc()}")
        
        # Show technical details for debugging
        with st.expander("Technical Details"):
            st.code(traceback.format_exc())
        
        # Provide a reset option
        if st.button("Reset Resume Enhancer"):
            for key in st.session_state.keys():
                if key.startswith("resume_"):
                    del st.session_state[key]
            st.rerun()

if __name__ == "__main__":
    main() 