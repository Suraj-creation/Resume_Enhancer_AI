import streamlit as st
import os
from datetime import datetime
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import time
import re
import numpy as np
import tempfile
import requests
import threading
from utils.supabase_client import get_supabase_client
from utils.db_utils import initialize_database
from utils.auth_utils import require_auth
from utils.resume_processor import extract_text_with_tika, extract_structured_data, find_missing_sections, extract_text_from_pdf as advanced_extract
from pages._init import render_step_indicator, render_section_title, render_info_box
import random

# Text analysis and grammar checking tools
TEXTBLOB_AVAILABLE = False
LANGUAGE_TOOL_AVAILABLE = False

try:
    from textblob import TextBlob
    TEXTBLOB_AVAILABLE = True
except ImportError:
    TEXTBLOB_AVAILABLE = False

try:
    import language_tool_python
    LANGUAGE_TOOL_AVAILABLE = True
    # Initialize the language tool once to avoid repeated startups
    language_tool = None
except ImportError:
    LANGUAGE_TOOL_AVAILABLE = False


def show_input_step():
    """Show the input step for resume job matching"""
    render_section_title("Upload Resume & Job Description", "Step 1: Upload your resume and enter job description", icon="📤")
    
    # Create two columns for information and upload
    info_col, upload_col = st.columns([1, 2])
    
    with info_col:
        # Information card
        st.markdown("""
        <div style="background: white; border-radius: 10px; padding: 1.5rem; margin-bottom: 1rem;
                   box-shadow: 0 4px 6px rgba(0,0,0,0.05), 0 1px 3px rgba(0,0,0,0.1);">
            <h4 style="margin-top: 0; color: #4361EE;">How This Works</h4>
            <ol style="padding-left: 1.2rem; margin: 1rem 0;">
                <li style="margin-bottom: 0.5rem;"><strong>Upload Resume</strong>: Upload your resume in PDF format</li>
                <li style="margin-bottom: 0.5rem;"><strong>Enter Job Description</strong>: Paste the job description</li>
                <li style="margin-bottom: 0.5rem;"><strong>AI Analysis</strong>: Our AI analyzes the match</li>
                <li><strong>Download</strong>: Get your optimized resume</li>
            </ol>
            <p style="margin: 0; font-size: 0.9rem; color: #6B7280;">
                For best results, use a well-formatted resume and detailed job description.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Add other information sections...
        
    with upload_col:
        # Resume upload handling...
        
        # Job description input with enhanced styling
        st.markdown("""
        <h3 style="margin-top: 2rem; font-size: 1.1rem; font-weight: 600; color: #1e293b;">Enter Job Description</h3>
        <p style="color: #64748b; font-size: 0.9rem; margin-bottom: 1rem;">Paste the complete job posting to analyze how well your resume matches</p>
        """, unsafe_allow_html=True)
        
        # Enhanced text area for job description
        job_description = st.text_area(
            "Paste the full job description here",
            value=st.session_state.get("job_description", ""),
            height=250,
            placeholder="Copy and paste the complete job description here for best matching results...",
            key="job_description_input"
        )
        
        # Update session state with job description
        if "job_description" not in st.session_state or job_description != st.session_state.job_description:
            st.session_state.job_description = job_description
        
        # Enhanced action button styling
        st.markdown("""
        <style>
            div.stButton > button:first-child {
            background-color: #4361EE;
            color: white;
                border: none;
                padding: 0.5rem 1.5rem;
                font-weight: 600;
                border-radius: 0.375rem;
                display: inline-flex;
                align-items: center;
                justify-content: center;
                transition: all 0.2s;
            }
            div.stButton > button:first-child:hover {
                background-color: #3b52c9;
                box-shadow: 0 4px 8px rgba(67, 97, 238, 0.2);
                transform: translateY(-1px);
            }
            div.stButton > button:first-child:active {
                transform: translateY(0px);
            }
        </style>
        """, unsafe_allow_html=True)
        
        # Cannot proceed without both resume and job description
        if st.session_state.get("resume_text_job", "") and st.session_state.get("job_description", ""):
            # Ready to proceed - show analyze button with icon
            if st.button("🔍 Analyze Job Match", key="analyze_job_match"):
                st.session_state.job_current_step = 2
                st.rerun()
        else:
            # Show what's missing with clear instructions
            no_file_message = ""
            if not st.session_state.get("resume_text_job", ""):
                no_file_message += "Please upload your resume. "
            if not st.session_state.get("job_description", ""):
                no_file_message += "Please enter a job description."
                
            if no_file_message:
                # Enhanced warning message
                render_info_box(no_file_message, box_type="warning")
                
                # Show a sample job description to help users
                if not st.session_state.get("job_description", ""):
                    with st.expander("Need a sample job description for testing?"):
                        st.markdown("""
                        ## Senior Python Developer
                        
                        **Company:** Tech Innovations Inc.
                        
                        **Location:** Chicago, IL (Remote available)
                        
                        **Job Description:**
                        We are seeking an experienced Python Developer to join our growing team. The ideal candidate will be responsible for developing and maintaining high-quality, scalable applications.
                        
                        **Responsibilities:**
                        - Design, develop, and maintain Python applications
                        - Write clean, maintainable, and efficient code
                        - Troubleshoot and fix bugs in existing applications
                        - Collaborate with cross-functional teams to define and design new features
                        - Implement security and data protection measures
                        
                        **Requirements:**
                        - 5+ years of experience with Python development
                        - Experience with web frameworks such as Django or Flask
                        - Knowledge of front-end technologies (JavaScript, HTML, CSS)
                        - Understanding of RESTful APIs
                        - Experience with SQL and NoSQL databases
                        - Strong problem-solving skills and attention to detail
                        - Bachelor's degree in Computer Science or equivalent experience
                        
                        **Nice to Have:**
                        - Experience with AWS or other cloud platforms
                        - Knowledge of Docker and Kubernetes
                        - Experience with CI/CD pipelines
                        - Machine Learning experience
                        
                        **Benefits:**
                        - Competitive salary
                        - Health, dental, and vision insurance
                        - 401(k) matching
                        - Flexible work hours
                        - Professional development opportunities
                        """)
                        
                        # Enhanced button for using sample
                        if st.button("✨ Use this Sample", key="use_sample_job_desc"):
                            st.session_state.job_description = """Senior Python Developer..."""
                            st.rerun()
                
                # Show resume tips
                with st.expander("Tips for optimizing your resume"):
                    st.markdown("""
                    ## Resume Optimization Tips
                    
                    1. **Tailor to the Job**: Customize your resume for each application
                    2. **Use Keywords**: Include industry and job-specific keywords
                    3. **Quantify Achievements**: Use numbers to demonstrate impact
                    4. **Be Concise**: Keep to 1-2 pages with clear formatting
                    5. **Include Relevant Skills**: List technical and soft skills that match the job
                    6. **Update Regularly**: Ensure all information is current
                    """)
                
                # Progressive guidance based on what's completed
                if st.session_state.get("resume_text_job", ""):
                    st.info("✅ Resume uploaded! Now enter a job description to continue.")
                elif st.session_state.get("job_description", ""):
                    st.info("✅ Job description entered! Now upload your resume to continue.") 