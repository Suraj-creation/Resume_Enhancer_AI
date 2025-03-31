"""
Resume Job Matching - Compare resume against job descriptions
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

# Try to import the required modules with fallbacks
try:
    # Import core modules
    from pages._init import render_step_indicator, render_section_title, render_info_box, initialize_session
    
    # Import resume processing utilities with fallbacks
    try:
        from utils.resume_processor import extract_text_from_pdf, extract_text_advanced
        resume_processor_available = True
    except ImportError as e:
        logger.error(f"Error importing resume_processor: {str(e)}")
        resume_processor_available = False
    
    # Import job matching utilities
    try:
        from utils.job_matching import (
            compare_resume_to_job, 
            extract_job_keywords, 
            get_missing_skills, 
            calculate_match_percentage,
            generate_improvement_suggestions
        )
        job_matching_available = True
    except ImportError as e:
        logger.error(f"Error importing job_matching: {str(e)}")
        job_matching_available = False
        
except ImportError as e:
    logger.error(f"Critical import error: {str(e)}")
    # We'll handle this in the main function

# Define the steps for the job matching flow
steps = [
    ("Upload Resume", "📤"),
    ("Add Job Description", "📋"),
    ("Match Analysis", "🔍"),
    ("Recommendations", "✨")
]

def initialize_job_match_state():
    """Initialize session state variables for the job matching"""
    # Initialize common session variables
    try:
        initialize_session()
    except:
        # Fallback if _init module is not available
        pass
    
    # Job matching specific state
    if 'resume_text' not in st.session_state:
        st.session_state.resume_text = ""
    
    if 'job_description' not in st.session_state:
        st.session_state.job_description = ""
    
    if 'job_matching_step' not in st.session_state:
        st.session_state.job_matching_step = 0  # Start at the upload step
    
    if 'matching_results' not in st.session_state:
        st.session_state.matching_results = {}

def set_step(step):
    """Set the current step in the job matching workflow"""
    st.session_state.job_matching_step = step
    st.rerun()

def show_upload_resume_step():
    """Show the resume upload step"""
    render_section_title("Upload Resume", "Step 1: Upload your resume to compare against job descriptions")
    
    # Instructions
    st.markdown("""
    Upload your resume (PDF format) to begin the job matching process. We'll extract the content and
    compare it against job descriptions to find the best match.
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
                progress_placeholder.text("Extracting text from resume...")
                progress_bar.progress(33)
                
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
                progress_placeholder.text("Resume processed successfully!")
                progress_bar.progress(100)
                
                # Show the resume text
                st.success("Resume uploaded successfully!")
                with st.expander("View Extracted Resume Text"):
                    st.text_area("Resume Content", resume_text, height=200, disabled=True)
                
                # Show button to continue
                if st.button("Next: Add Job Description →"):
                    set_step(1)
                
            except Exception as e:
                st.error(f"Error processing resume: {str(e)}")
                logger.error(f"Error processing resume: {traceback.format_exc()}")
    
    # Use existing resume if available
    elif st.session_state.resume_text:
        st.success("Resume already loaded!")
        with st.expander("View Loaded Resume Text"):
            st.text_area("Resume Content", st.session_state.resume_text, height=200, disabled=True)
        
        if st.button("Next: Add Job Description →"):
            set_step(1)
    
    # Demo option
    st.markdown("---")
    if st.button("Try Demo Resume"):
        # Load demo resume
        demo_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "sample_resume.pdf")
        if os.path.exists(demo_path):
            with st.spinner("Loading demo resume..."):
                st.session_state.resume_file_path = demo_path
                
                # Extract text
                if resume_processor_available:
                    resume_text, _ = extract_text_advanced(demo_path)
                    if not resume_text:
                        resume_text = extract_text_from_pdf(demo_path)
                else:
                    # Basic fallback if module not available
                    import PyPDF2
                    with open(demo_path, 'rb') as file:
                        reader = PyPDF2.PdfReader(file)
                        resume_text = ""
                        for page in reader.pages:
                            resume_text += page.extract_text() + "\n"
                
                st.session_state.resume_text = resume_text
                st.success("Demo resume loaded successfully!")
                
                # Show the resume text
                with st.expander("View Demo Resume Text"):
                    st.text_area("Resume Content", resume_text, height=200, disabled=True)
                
                # Show button to continue
                if st.button("Continue with Demo Resume"):
                    set_step(1)
        else:
            st.error("Demo resume not found. Please upload your own resume.")

def show_job_description_step():
    """Show the job description input step"""
    render_section_title("Job Description", "Step 2: Enter or paste a job description")
    
    # Check if resume is uploaded
    if not st.session_state.resume_text:
        st.warning("Please upload your resume first.")
        if st.button("← Go Back to Upload Resume"):
            set_step(0)
        return
    
    # Instructions
    st.markdown("""
    Enter or paste a job description to compare with your resume. You can either:
    - Paste a job description directly
    - Upload a job description file
    - Use one of our sample job descriptions
    """)
    
    # Input tabs
    tab1, tab2, tab3 = st.tabs(["Paste Job Description", "Upload File", "Sample Jobs"])
    
    with tab1:
        # Text area for job description
        job_description = st.text_area(
            "Enter job description",
            value=st.session_state.job_description,
            height=300,
            placeholder="Paste the job description here..."
        )
        
        if job_description:
            st.session_state.job_description = job_description
            
            if st.button("Analyze Match →", key="analyze_pasted"):
                set_step(2)
    
    with tab2:
        # File uploader for job description
        uploaded_file = st.file_uploader(
            "Upload job description file",
            type=["pdf", "txt", "docx"],
            help="Upload a job description file"
        )
        
        if uploaded_file:
            try:
                # Extract text based on file type
                if uploaded_file.name.endswith('.pdf'):
                    if resume_processor_available:
                        job_text, _ = extract_text_advanced(uploaded_file)
                        if not job_text:
                            job_text = extract_text_from_pdf(uploaded_file)
                    else:
                        # Basic fallback
                        import PyPDF2
                        reader = PyPDF2.PdfReader(uploaded_file)
                        job_text = ""
                        for page in reader.pages:
                            job_text += page.extract_text() + "\n"
                elif uploaded_file.name.endswith('.txt'):
                    job_text = uploaded_file.getvalue().decode('utf-8')
                elif uploaded_file.name.endswith('.docx'):
                    try:
                        import docx
                        doc = docx.Document(uploaded_file)
                        job_text = "\n".join([para.text for para in doc.paragraphs])
                    except ImportError:
                        st.error("Python-docx module not available. Please paste the job description instead.")
                        job_text = ""
                else:
                    job_text = uploaded_file.getvalue().decode('utf-8')
                
                if job_text:
                    st.session_state.job_description = job_text
                    st.success("Job description loaded!")
                    
                    # Show the job description
                    with st.expander("View Job Description"):
                        st.text_area("Content", job_text, height=200, disabled=True)
                    
                    if st.button("Analyze Match →", key="analyze_uploaded"):
                        set_step(2)
            except Exception as e:
                st.error(f"Error processing file: {str(e)}")
    
    with tab3:
        # Sample job descriptions
        sample_jobs = {
            "Software Engineer": """
            Software Engineer
            
            Requirements:
            - 3+ years of experience with Python, JavaScript, or Java
            - Experience with web frameworks (Django, Flask, React, Angular)
            - Understanding of databases (SQL and NoSQL)
            - Knowledge of cloud platforms (AWS, GCP, Azure)
            - Bachelor's degree in Computer Science or related field
            
            Responsibilities:
            - Develop and maintain web applications
            - Collaborate with cross-functional teams
            - Write clean, maintainable, and efficient code
            - Participate in code reviews and mentor junior developers
            """,
            
            "Data Scientist": """
            Data Scientist
            
            Requirements:
            - Strong programming skills in Python, R, or similar
            - Experience with data analysis and statistical modeling
            - Knowledge of machine learning algorithms and techniques
            - Familiarity with data visualization tools
            - Master's degree in Statistics, Computer Science, or related field
            
            Responsibilities:
            - Analyze large datasets to extract insights
            - Build and deploy machine learning models
            - Communicate findings to stakeholders
            - Stay current with the latest ML research and tools
            """,
            
            "Product Manager": """
            Product Manager
            
            Requirements:
            - 4+ years of experience in product management
            - Strong analytical and problem-solving skills
            - Excellent communication and leadership abilities
            - Experience with agile development methodologies
            - Bachelor's degree in Business, Engineering, or related field
            
            Responsibilities:
            - Define product vision, strategy, and roadmap
            - Gather and prioritize product requirements
            - Work closely with engineering, design, and marketing teams
            - Analyze market trends and competitive landscape
            """
        }
        
        selected_job = st.selectbox(
            "Select a sample job description",
            options=list(sample_jobs.keys())
        )
        
        if st.button("Use This Job Description"):
            st.session_state.job_description = sample_jobs[selected_job]
            st.success(f"Sample job description for '{selected_job}' loaded!")
            
            # Show the job description
            with st.expander("View Job Description"):
                st.text_area("Content", sample_jobs[selected_job], height=200, disabled=True)
            
            if st.button("Analyze Match →", key="analyze_sample"):
                set_step(2)
    
    # Navigation
    if st.button("← Back to Resume Upload"):
        set_step(0)

def show_match_analysis_step():
    """Show the match analysis step"""
    render_section_title("Match Analysis", "Step 3: Analyze how well your resume matches the job")
    
    # Check if both resume and job description are available
    if not st.session_state.resume_text:
        st.warning("Please upload your resume first.")
        if st.button("← Go Back to Upload Resume"):
            set_step(0)
        return
    
    if not st.session_state.job_description:
        st.warning("Please add a job description.")
        if st.button("← Go Back to Add Job Description"):
            set_step(1)
        return
    
    # Run the matching analysis
    with st.spinner("Analyzing match..."):
        if job_matching_available:
            # Use the job matching module
            try:
                # Run the analysis
                match_results = compare_resume_to_job(
                    st.session_state.resume_text,
                    st.session_state.job_description
                )
                
                # Store results in session state
                st.session_state.matching_results = match_results
                
                # Calculate match percentage
                match_percentage = calculate_match_percentage(
                    st.session_state.resume_text,
                    st.session_state.job_description
                )
                
                # Get missing skills
                missing_skills = get_missing_skills(
                    st.session_state.resume_text,
                    st.session_state.job_description
                )
                
                # Generate suggestions
                suggestions = generate_improvement_suggestions(
                    st.session_state.resume_text,
                    st.session_state.job_description
                )
                
                st.session_state.match_percentage = match_percentage
                st.session_state.missing_skills = missing_skills
                st.session_state.job_suggestions = suggestions
                
            except Exception as e:
                st.error(f"Error running job matching: {str(e)}")
                logger.error(f"Error in job matching: {traceback.format_exc()}")
                
                # Fallback to basic analysis
                job_matching_available = False
        
        if not job_matching_available:
            # Basic fallback analysis
            try:
                import re
                from collections import Counter
                
                # Extract keywords from job description
                def extract_basic_keywords(text):
                    # Remove special chars and convert to lowercase
                    text = re.sub(r'[^\w\s]', ' ', text.lower())
                    # Split into words
                    words = text.split()
                    # Remove common words
                    common_words = {'and', 'the', 'to', 'of', 'in', 'with', 'for', 'a', 'an', 'is', 'are', 'on', 'or', 'as', 'by'}
                    words = [word for word in words if word not in common_words and len(word) > 2]
                    # Count word frequency
                    word_counts = Counter(words)
                    # Return most common words
                    return dict(word_counts.most_common(20))
                
                # Extract keywords from both
                job_keywords = extract_basic_keywords(st.session_state.job_description)
                resume_keywords = extract_basic_keywords(st.session_state.resume_text)
                
                # Find matching keywords
                matching_keywords = []
                for keyword in job_keywords:
                    if keyword in resume_keywords:
                        matching_keywords.append(keyword)
                
                # Calculate simple match percentage
                if job_keywords:
                    match_percentage = (len(matching_keywords) / len(job_keywords)) * 100
                else:
                    match_percentage = 0
                
                # Find missing keywords
                missing_keywords = []
                for keyword in job_keywords:
                    if keyword not in resume_keywords:
                        missing_keywords.append(keyword)
                
                # Store results
                st.session_state.match_percentage = match_percentage
                st.session_state.matching_results = {
                    'job_keywords': job_keywords,
                    'resume_keywords': resume_keywords,
                    'matching_keywords': matching_keywords
                }
                st.session_state.missing_skills = missing_keywords
                st.session_state.job_suggestions = [
                    f"Consider adding these keywords to your resume: {', '.join(missing_keywords[:5])}"
                ]
                
            except Exception as e:
                st.error(f"Error in basic analysis: {str(e)}")
                logger.error(f"Error in basic analysis: {traceback.format_exc()}")
                
                # Set default values
                st.session_state.match_percentage = 0
                st.session_state.matching_results = {}
                st.session_state.missing_skills = []
                st.session_state.job_suggestions = []
    
    # Display match percentage
    st.markdown("### Match Score")
    
    # Show percentage with gauge
    col1, col2 = st.columns([1, 2])
    with col1:
        # Create a progress bar/gauge
        match_score = st.session_state.match_percentage
        st.progress(min(match_score/100, 1.0))
    with col2:
        # Show text description based on score
        st.markdown(f"**{match_score:.1f}%** match with this job description")
        if match_score >= 80:
            st.success("Excellent match! Your resume aligns very well with this job.")
        elif match_score >= 60:
            st.info("Good match! Your resume covers most of the key requirements.")
        elif match_score >= 40:
            st.warning("Fair match. Consider enhancing your resume to better target this job.")
        else:
            st.error("Low match. Your resume may need significant updates for this position.")
    
    # Display keyword analysis
    with st.expander("Keyword Analysis", expanded=True):
        st.markdown("### Keywords from Job Description")
        
        # Show matching and missing keywords
        if 'matching_results' in st.session_state and st.session_state.matching_results:
            # Show keywords found in both
            if 'matching_keywords' in st.session_state.matching_results:
                matching = st.session_state.matching_results['matching_keywords']
                if matching:
                    st.markdown("#### Keywords Found in Your Resume")
                    keyword_str = ", ".join(matching[:10])  # Limit to first 10
                    render_info_box(keyword_str, "success")
            
            # Show missing keywords
            if st.session_state.missing_skills:
                st.markdown("#### Keywords Missing from Your Resume")
                missing_str = ", ".join(st.session_state.missing_skills[:10])  # Limit to first 10
                render_info_box(missing_str, "warning")
    
    # Navigation buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Back to Job Description"):
            set_step(1)
    with col2:
        if st.button("Next: Recommendations →"):
            set_step(3)

def show_recommendations_step():
    """Show the recommendations step"""
    render_section_title("Recommendations", "Step 4: Get suggestions to improve your match")
    
    # Check if we have analysis results
    if not st.session_state.matching_results:
        st.warning("Please complete the match analysis first.")
        if st.button("← Go Back to Match Analysis"):
            set_step(2)
        return
    
    # Display recommendations
    st.markdown("### How to Improve Your Resume")
    
    # Show suggestions
    if 'job_suggestions' in st.session_state and st.session_state.job_suggestions:
        for i, suggestion in enumerate(st.session_state.job_suggestions):
            render_info_box(suggestion, "info")
    
    # Missing skills section
    if 'missing_skills' in st.session_state and st.session_state.missing_skills:
        with st.expander("Skills to Highlight", expanded=True):
            st.markdown("### Key Skills to Add or Emphasize")
            
            for skill in st.session_state.missing_skills[:10]:  # Limit to top 10
                st.markdown(f"- **{skill}**")
            
            st.markdown("""
            **Tips for adding skills:**
            - Only include skills you actually possess
            - Provide examples of how you've used these skills
            - Quantify your experience when possible
            """)
    
    # Job-specific resume tips
    with st.expander("Job-Specific Resume Tips", expanded=True):
        st.markdown("### Tailoring Your Resume for This Job")
        
        st.markdown("""
        1. **Customize your summary/objective** to highlight relevant experience
        2. **Reorder your experience** to put the most relevant experience first
        3. **Use similar terminology** as found in the job description
        4. **Highlight achievements** that demonstrate required skills
        5. **Remove irrelevant information** to keep focus on what matters for this job
        """)
    
    # Generate tailored resume section
    st.markdown("### Generate a Tailored Resume")
    
    st.info("""
    Want to automatically create a tailored version of your resume for this job? 
    Our AI can help you highlight relevant experience and skills.
    """)
    
    if st.button("Generate Tailored Resume"):
        with st.spinner("Generating tailored resume..."):
            # Placeholder for resume generation functionality
            time.sleep(2)
            st.success("Feature coming soon! This will generate a tailored version of your resume.")
    
    # Navigation buttons
    if st.button("← Back to Match Analysis"):
        set_step(2)
    
    # Start over button
    st.markdown("---")
    if st.button("Start Over with New Job"):
        # Reset job description and analysis results
        st.session_state.job_description = ""
        st.session_state.matching_results = {}
        st.session_state.match_percentage = 0
        st.session_state.missing_skills = []
        st.session_state.job_suggestions = []
        
        # Go back to job description step
        set_step(1)

def main():
    """Main entry point for resume job matching page"""
    try:
        # Initialize variables if needed
        initialize_job_match_state()
        
        # Page title and description
        st.title("Resume Job Matching")
        
        # Show step indicator
        render_step_indicator(steps, st.session_state.job_matching_step)
        
        # Display current step based on session state
        if st.session_state.job_matching_step == 0:
            show_upload_resume_step()
        elif st.session_state.job_matching_step == 1:
            show_job_description_step()
        elif st.session_state.job_matching_step == 2:
            show_match_analysis_step()
        elif st.session_state.job_matching_step == 3:
            show_recommendations_step()
            
    except Exception as e:
        st.error(f"An error occurred in the Resume Job Matching: {str(e)}")
        logger.error(f"Error in Resume Job Matching: {traceback.format_exc()}")
        
        # Show technical details for debugging
        with st.expander("Technical Details"):
            st.code(traceback.format_exc())
        
        # Provide a reset option
        if st.button("Reset Job Matching"):
            for key in st.session_state.keys():
                if key.startswith("job_") or key in ["matching_results", "match_percentage", "missing_skills"]:
                    del st.session_state[key]
            st.rerun()

if __name__ == "__main__":
    main()
