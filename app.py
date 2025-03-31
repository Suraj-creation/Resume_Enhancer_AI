"""
Resume AI - Main application entry point
"""
import streamlit as st

# Set page configuration as the first Streamlit command for optimal loading
st.set_page_config(
    page_title="Resume AI",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

import sys
import logging
import os
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Function to lazy load modules 
@st.cache_resource
def get_module(module_name):
    """
    Dynamically import and return a module.
    This improves startup time by only loading modules when needed.
    """
    try:
        if module_name == "pandas":
            import pandas as pd
            return pd
        elif module_name == "json":
            import json
            return json
        elif module_name == "os":
            import os
            return os
        elif module_name == "tempfile":
            import tempfile
            return tempfile
        elif module_name == "shutil":
            import shutil
            return shutil
        elif module_name == "components":
            from utils.components import (
                loading_spinner, 
                progress_bar, 
                sidebar_info, 
                feature_card,
                testimonial_card
            )
            return {
                "loading_spinner": loading_spinner,
                "progress_bar": progress_bar,
                "sidebar_info": sidebar_info,
                "feature_card": feature_card,
                "testimonial_card": testimonial_card
            }
        elif module_name == "resume_enhancer":
            # Try to import from _resume_enhancer.py (the underscore file is the actual implementation)
            try:
                from pages._resume_enhancer import main as resume_enhancer_main
                return resume_enhancer_main
            except ImportError:
                # Fallback to the non-underscore version
                from pages.resume_enhancer import main as resume_enhancer_main
                return resume_enhancer_main
        elif module_name == "resume_job_matching":
            try:
                from pages._resume_job_matching import main as resume_job_matching_main
                return resume_job_matching_main
            except ImportError:
                # Fallback to fixed version if available
                try:
                    from pages._resume_job_matching_fixed import main as resume_job_matching_main
                    return resume_job_matching_main
                except ImportError:
                    logger.error("Could not load resume_job_matching module from any source")
                    return None
        elif module_name == "auth":
            from pages._auth import (
                check_authentication,
                render_login_ui,
                render_signup_ui,
                logout
            )
            return {
                "check_authentication": check_authentication,
                "render_login_ui": render_login_ui,
                "render_signup_ui": render_signup_ui,
                "logout": logout
            }
        elif module_name == "ai_services":
            from utils.ai_services import AIServiceManager
            return AIServiceManager()
    except Exception as e:
        logger.error(f"Error loading module {module_name}: {str(e)}")
        return None

# Add minimal CSS for initial rendering - more styles can be loaded on demand
def load_minimal_css():
    return """
    <style>
    .main-header {
        text-align: center;
        margin-bottom: 30px;
    }
    .feature-container {
        display: flex;
        flex-wrap: wrap;
        justify-content: center;
        gap: 20px;
        margin-bottom: 40px;
    }
    .app-footer {
        text-align: center;
        margin-top: 50px;
        padding: 20px;
        font-size: 0.8em;
    }
    /* Hide hamburger menu and footer */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """

# Initialize session state
def initialize_session_state():
    """Initialize session state variables"""
    if "page" not in st.session_state:
        st.session_state.page = "home"
        
    if "loaded_modules" not in st.session_state:
        st.session_state.loaded_modules = {}
    
    # Initialize authentication state
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
        
    if "auth_page" not in st.session_state:
        st.session_state.auth_page = "login"
    
    # Initialize other required session state variables
    if "resume_text" not in st.session_state:
        st.session_state.resume_text = ""
    
    if "job_description" not in st.session_state:
        st.session_state.job_description = ""
        
    # Create necessary directories if they don't exist
    os.makedirs("data", exist_ok=True)
    os.makedirs("templates", exist_ok=True)
    os.makedirs("images", exist_ok=True)

def main():
    """Main application entry point"""
    # Load minimal CSS
    st.markdown(load_minimal_css(), unsafe_allow_html=True)
    
    # Initialize session state
    initialize_session_state()
    
    # Lazy load authentication module
    if "auth" not in st.session_state.loaded_modules:
        st.session_state.loaded_modules["auth"] = get_module("auth")
    
    auth_module = st.session_state.loaded_modules.get("auth")
    
    # Handle authentication
    if not st.session_state.authenticated:
        authenticated = auth_module["check_authentication"]() if auth_module else False
        st.session_state.authenticated = authenticated
    
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
                # Preload necessary module before page change
                if "resume_enhancer" not in st.session_state.loaded_modules:
                    with st.spinner("Loading Resume Enhancer..."):
                        st.session_state.loaded_modules["resume_enhancer"] = get_module("resume_enhancer")
                st.rerun()
            
            if st.button("🎯 Job Matching", use_container_width=True):
                st.session_state.page = "job_matching"
                # Preload necessary module before page change
                if "resume_job_matching" not in st.session_state.loaded_modules:
                    with st.spinner("Loading Job Matching..."):
                        st.session_state.loaded_modules["resume_job_matching"] = get_module("resume_job_matching")
                st.rerun()
            
            st.markdown("---")
            
            # Logout button
            if st.button("🚪 Logout", use_container_width=True):
                if auth_module:
                    auth_module["logout"]()
                else:
                    st.session_state.authenticated = False
                st.rerun()
        else:
            # User is not logged in, show auth options
            if st.session_state.auth_page == "login":
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
        if auth_module:
            if st.session_state.auth_page == "login":
                auth_module["render_login_ui"]()
            else:
                auth_module["render_signup_ui"]()
        else:
            st.error("Authentication module not available")
            
            # Provide a demo login option
            if st.button("Try Demo Mode"):
                st.session_state.authenticated = True
                st.session_state.user_id = "demo-user"
                st.session_state.user_name = "Demo User"
                st.rerun()
    else:
        # User is authenticated, show the requested page
        if st.session_state.page == "home":
            show_home_page()
        elif st.session_state.page == "resume_enhancer":
            resume_enhancer = st.session_state.loaded_modules.get("resume_enhancer")
            if resume_enhancer:
                resume_enhancer()
            else:
                st.error("Resume Enhancer module failed to load. Please refresh the page and try again.")
                # Provide a reload option
                if st.button("Reload Resume Enhancer"):
                    st.session_state.loaded_modules["resume_enhancer"] = get_module("resume_enhancer")
                    st.rerun()
        elif st.session_state.page == "job_matching":
            resume_job_matching = st.session_state.loaded_modules.get("resume_job_matching")
            if resume_job_matching:
                resume_job_matching()
            else:
                st.error("Job Matching module failed to load. Please refresh the page and try again.")
                # Provide a reload option
                if st.button("Reload Job Matching"):
                    st.session_state.loaded_modules["resume_job_matching"] = get_module("resume_job_matching")
                    st.rerun()

@st.cache_data(ttl=3600, show_spinner=False)
def get_feature_data():
    """Return feature data for the home page - cached to avoid rebuilding"""
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
    
    # Hero section (kept minimal for faster loading)
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
    
    # Lazy load components module if needed
    if "components" not in st.session_state.loaded_modules:
        st.session_state.loaded_modules["components"] = get_module("components")
    
    components = st.session_state.loaded_modules.get("components")
    features = get_feature_data()
    
    # Display features in columns
    cols = st.columns(len(features))
    
    for i, feature in enumerate(features):
        with cols[i]:
            if components:
                # Use the feature card component
                components["feature_card"](
                    title=feature["title"],
                    description=feature["description"],
                    icon=feature["icon"],
                    on_click=lambda p=feature["page"]: set_page(p)
                )
            else:
                # Fallback if components module failed to load
                st.markdown(f"""
                <div style='border: 1px solid #ddd; padding: 20px; border-radius: 5px;'>
                    <h3>{feature['icon']} {feature['title']}</h3>
                    <p>{feature['description']}</p>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"Try {feature['title']}", key=f"btn_{feature['page']}"):
                    set_page(feature["page"])
    
    # Testimonials section (simplified for performance)
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