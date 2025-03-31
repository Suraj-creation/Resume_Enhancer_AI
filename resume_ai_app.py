"""
Resume AI - All-in-one application
"""
import streamlit as st
import os
import sys
import time
import re
import logging
import math
import tempfile
import traceback
from pathlib import Path
from datetime import datetime
from collections import Counter
from typing import Dict, List, Set, Tuple, Any, Optional

# Set page configuration as the first Streamlit command for optimal loading
st.set_page_config(
    page_title="Resume AI",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

#####################################################################
# Custom CSS and UI Components
#####################################################################

def load_css():
    """Load custom CSS for styling the app"""
    return """
    <style>
    /* General styling */
    body {
        font-family: 'Inter', sans-serif;
        background-color: #f8f9fa;
    }
    
    /* Button styling */
    .stButton button {
        background-color: #4361EE;
        color: white;
        border-radius: 6px;
        padding: 0.5rem 1rem;
        font-weight: 500;
        border: none;
        transition: all 0.3s ease;
    }
    .stButton button:hover {
        background-color: #3A56D4;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    
    /* Form styling */
    .stTextInput input, .stNumberInput input, .stSelectbox, .stTextArea textarea {
        border-radius: 6px;
        border: 1px solid #ddd;
        padding: 8px 12px;
    }
    .stTextInput input:focus, .stNumberInput input:focus, .stSelectbox:focus, .stTextArea textarea:focus {
        border-color: #4361EE;
        box-shadow: 0 0 0 1px #4361EE;
    }
    
    /* Card styling */
    .card {
        background-color: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .card:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.1);
    }
    
    /* Progress bar styling */
    .stProgress .st-bo {
        background-color: #4361EE;
    }
    
    /* Hide hamburger menu and footer */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Custom header styling */
    .main-header {
        font-size: 2.3rem;
        font-weight: 700;
        color: #1E293B;
        margin-bottom: 1rem;
    }
    
    .sub-header {
        font-size: 1.6rem;
        font-weight: 600;
        color: #334155;
        margin-bottom: 0.75rem;
    }
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 1rem;
    }
    .stTabs [data-baseweb="tab"] {
        height: 3rem;
        border-radius: 6px 6px 0 0;
        padding: 0 1rem;
        font-weight: 500;
    }
    .stTabs [aria-selected="true"] {
        background-color: #4361EE !important;
        color: white !important;
    }
    
    /* Custom badges */
    .badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 500;
        line-height: 1;
    }
    .badge-blue {
        background-color: rgba(67, 97, 238, 0.1);
        color: #4361EE;
    }
    .badge-green {
        background-color: rgba(16, 185, 129, 0.1);
        color: #10B981;
    }
    .badge-red {
        background-color: rgba(239, 68, 68, 0.1);
        color: #EF4444;
    }
    </style>
    """

def render_feature_card(title, description, icon, button_text="Get Started", on_click=None):
    """Render a feature card with consistent styling"""
    st.markdown(f"""
    <div class="card">
        <div style="display: flex; align-items: center; margin-bottom: 1rem;">
            <div style="background-color: rgba(67, 97, 238, 0.1); border-radius: 12px; width: 42px; height: 42px; 
                        display: flex; align-items: center; justify-content: center; margin-right: 1rem;">
                <span style="font-size: 1.5rem;">{icon}</span>
            </div>
            <h3 style="margin: 0; font-size: 1.2rem; font-weight: 600; color: #1E293B;">{title}</h3>
        </div>
        <p style="color: #64748B; margin-bottom: 1.5rem; font-size: 0.95rem;">{description}</p>
    </div>
    """, unsafe_allow_html=True)
    
    if button_text:
        if on_click:
            st.button(button_text, key=f"btn_{title.replace(' ', '_').lower()}", on_click=on_click)
        else:
            st.button(button_text, key=f"btn_{title.replace(' ', '_').lower()}")

def render_step_indicator(steps, current_step=0):
    """
    Render a step indicator for a multi-step process
    
    Args:
        steps (list): List of (step_name, step_icon) tuples
        current_step (int): Index of the current step (0-based)
    """
    # Create a container for the steps
    cols = st.columns(len(steps))
    
    for i, (step_name, step_icon) in enumerate(steps):
        with cols[i]:
            if i < current_step:
                # Completed step
                st.markdown(f"""
                <div style='text-align: center; color: #4CAF50;'>
                    <div style='font-size: 1.5rem; margin-bottom: 5px;'>✅</div>
                    <div style='font-size: 0.8rem;'>{step_name}</div>
                </div>
                """, unsafe_allow_html=True)
            elif i == current_step:
                # Current step
                st.markdown(f"""
                <div style='text-align: center; color: #2196F3;'>
                    <div style='font-size: 1.5rem; margin-bottom: 5px;'>{step_icon}</div>
                    <div style='font-size: 0.8rem; font-weight: bold;'>{step_name}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                # Future step
                st.markdown(f"""
                <div style='text-align: center; color: #9E9E9E;'>
                    <div style='font-size: 1.5rem; margin-bottom: 5px;'>{step_icon}</div>
                    <div style='font-size: 0.8rem;'>{step_name}</div>
                </div>
                """, unsafe_allow_html=True)
    
    # Add a separator
    st.markdown("<hr>", unsafe_allow_html=True)

def render_section_title(title, subtitle=None, icon=None):
    """
    Render a section title with optional subtitle and icon
    
    Args:
        title (str): The section title
        subtitle (str): Optional subtitle
        icon (str): Optional icon
    """
    if icon:
        title = f"{icon} {title}"
    
    st.markdown(f"## {title}")
    
    if subtitle:
        st.markdown(f"*{subtitle}*")
    
    # Add some space
    st.write("")

def render_info_box(content, box_type="info"):
    """
    Render an info box
    
    Args:
        content (str): Content to display
        box_type (str): Type of box (info, success, warning, error)
    """
    if box_type == "info":
        st.info(content)
    elif box_type == "success":
        st.success(content)
    elif box_type == "warning":
        st.warning(content)
    elif box_type == "error":
        st.error(content)

def render_card(title, content, icon=None, is_expanded=False):
    """Render a card-like expander with custom styling"""
    if icon:
        title = f"{icon} {title}"
    
    with st.expander(title, expanded=is_expanded):
        st.markdown(content)

def initialize_session():
    """Initialize basic session state variables"""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    
    if "user_id" not in st.session_state:
        st.session_state.user_id = None
    
    if "user_name" not in st.session_state:
        st.session_state.user_name = None
        
    if "page" not in st.session_state:
        st.session_state.page = "home"
        
    # Create necessary directories if they don't exist
    os.makedirs("data", exist_ok=True)
    os.makedirs("templates", exist_ok=True)
    os.makedirs("images", exist_ok=True)

#####################################################################
# Authentication Functions
#####################################################################

def check_authentication():
    """Check if the user is authenticated"""
    if st.session_state.get("authenticated", False):
        return True
    return False

def render_login_ui():
    """Render the login UI"""
    st.markdown("<h1 class='main-header'>Resume AI</h1>", unsafe_allow_html=True)
    st.markdown("<h2 class='sub-header'>Sign In</h2>", unsafe_allow_html=True)
    
    # Login form
    with st.form("login_form"):
        email = st.text_input("Email Address", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")
        submit = st.form_submit_button("Sign In")
        
        if submit:
            # For demonstration, accept any login
            if email and password:
                st.session_state.authenticated = True
                st.session_state.user_id = "user-" + email.split("@")[0]
                st.session_state.user_name = email.split("@")[0].capitalize()
                st.rerun()
            else:
                st.error("Please enter both email and password")
    
    # Demo login option
    st.markdown("---")
    if st.button("Try Demo Mode"):
        st.session_state.authenticated = True
        st.session_state.user_id = "demo-user"
        st.session_state.user_name = "Demo User"
        st.rerun()

def render_signup_ui():
    """Render the signup UI"""
    st.markdown("<h1 class='main-header'>Resume AI</h1>", unsafe_allow_html=True)
    st.markdown("<h2 class='sub-header'>Create Account</h2>", unsafe_allow_html=True)
    
    # Signup form
    with st.form("signup_form"):
        name = st.text_input("Full Name", key="signup_name")
        email = st.text_input("Email Address", key="signup_email")
        password = st.text_input("Password", type="password", key="signup_password")
        confirm_password = st.text_input("Confirm Password", type="password", key="signup_confirm_password")
        submit = st.form_submit_button("Create Account")
        
        if submit:
            # Simple validation
            if not name or not email or not password:
                st.error("Please fill in all fields")
            elif password != confirm_password:
                st.error("Passwords do not match")
            elif "@" not in email or "." not in email:
                st.error("Please enter a valid email address")
            else:
                # For demonstration, accept any signup
                st.session_state.authenticated = True
                st.session_state.user_id = "user-" + email.split("@")[0]
                st.session_state.user_name = name.split()[0]
                st.success("Account created successfully!")
                st.rerun()

def logout():
    """Log out the user"""
    st.session_state.authenticated = False
    st.session_state.user_id = None
    st.session_state.user_name = None
    st.session_state.page = "home"

#####################################################################
# Main Application Entry Point
#####################################################################

def main():
    """Main application entry point"""
    # Apply CSS
    st.markdown(load_css(), unsafe_allow_html=True)
    
    # Initialize session state
    initialize_session()
    
    # Sidebar navigation
    with st.sidebar:
        st.title("Resume AI")
        
        st.markdown("---")
        
        if st.session_state.authenticated:
            # User is logged in, show navigation options
            st.markdown(f"👤 **{st.session_state.get('user_name', 'User')}**")
            st.markdown("---")
            
            # Navigation buttons
            if st.button("🏠 Home", use_container_width=True):
                st.session_state.page = "home"
                st.rerun()
            
            if st.button("📝 Resume Enhancer", use_container_width=True):
                st.session_state.page = "resume_enhancer"
                st.rerun()
            
            if st.button("🎯 Job Matching", use_container_width=True):
                st.session_state.page = "job_matching"
                st.rerun()
            
            st.markdown("---")
            
            # Logout button
            if st.button("🚪 Logout", use_container_width=True):
                logout()
                st.rerun()
        else:
            # User is not logged in, show auth options
            if st.session_state.get("auth_page", "login") == "login":
                if st.button("Create Account", use_container_width=True):
                    st.session_state.auth_page = "signup"
                    st.rerun()
            else:
                if st.button("Login", use_container_width=True):
                    st.session_state.auth_page = "login"
                    st.rerun()
        
        # App info
        st.markdown("### About")
        st.markdown("""
        Resume AI uses artificial intelligence to help you create better resumes 
        and match them to job descriptions.
        """)
        
        st.markdown("### Version")
        st.markdown("v1.0.0")
    
    # Main content area
    if not st.session_state.authenticated:
        # Show authentication pages
        if st.session_state.get("auth_page", "login") == "login":
            render_login_ui()
        else:
            render_signup_ui()
    else:
        # User is authenticated, show the requested page
        if st.session_state.page == "home":
            show_home_page()
        elif st.session_state.page == "resume_enhancer":
            resume_enhancer_main()
        elif st.session_state.page == "job_matching":
            resume_job_matching_main()

def get_feature_data():
    """Return feature data for the home page"""
    return [
        {
            "title": "Resume Enhancer",
            "description": "Upload your resume and get AI-powered suggestions to enhance each section.",
            "icon": "📝",
            "page": "resume_enhancer"
        },
        {
            "title": "Job Matching",
            "description": "Compare your resume against job descriptions to see how well you match.",
            "icon": "🎯",
            "page": "job_matching"
        }
    ]

def show_home_page():
    """Display the home page"""
    st.markdown("<h1 class='main-header'>Resume AI</h1>", unsafe_allow_html=True)
    
    # Hero section
    st.markdown("""
    <div style='text-align: center; margin-bottom: 40px;'>
        <h2>Enhance Your Resume with AI</h2>
        <p>
            Resume AI uses artificial intelligence to help you create better resumes
            and match them to job descriptions.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Feature cards
    st.markdown("<h2>Features</h2>", unsafe_allow_html=True)
    features = get_feature_data()
    
    # Display features in columns
    cols = st.columns(len(features))
    
    for i, feature in enumerate(features):
        with cols[i]:
            render_feature_card(
                title=feature["title"],
                description=feature["description"],
                icon=feature["icon"],
                on_click=lambda p=feature["page"]: set_page(p)
            )
    
    # Testimonials section
    st.markdown("<h2>What Users Say</h2>", unsafe_allow_html=True)
    
    testimonial = {
        "quote": "Resume AI helped me customize my resume for each job application, significantly increasing my interview rate!",
        "author": "Sarah J., Software Engineer"
    }
    
    # Display testimonial with minimal styling
    st.markdown(f"""
    <div style='border-left: 3px solid #4CAF50; padding-left: 15px; margin: 20px 0;'>
        <p><em>"{testimonial['quote']}"</em></p>
        <p>— {testimonial['author']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Footer
    st.markdown("""
    <div class='app-footer'>
        <p>© 2023 Resume AI. All rights reserved.</p>
    </div>
    """, unsafe_allow_html=True)

def set_page(page_name):
    """Set the current page in session state and trigger a rerun"""
    st.session_state.page = page_name
    st.rerun()

if __name__ == "__main__":
    main() 