# Hidden from navigation with underscore prefix
# Initialization file for pages package

# This imports common utilities and setups for pages
import streamlit as st

# Set consistent page configuration
def setup_page_config():
    """Set consistent page configuration for all pages"""
    # Skip st.set_page_config() call since it's already called in app.py
    # Just apply the CSS
    
    # Apply custom CSS for better UI
    st.markdown("""
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
    
    /* Tooltip style */
    .tooltip {
        position: relative;
        display: inline-block;
        cursor: pointer;
    }
    .tooltip .tooltiptext {
        visibility: hidden;
        width: 200px;
        background-color: #333;
        color: #fff;
        text-align: center;
        border-radius: 6px;
        padding: 5px;
        position: absolute;
        z-index: 1;
        bottom: 125%;
        left: 50%;
        margin-left: -100px;
        opacity: 0;
        transition: opacity 0.3s;
    }
    .tooltip:hover .tooltiptext {
        visibility: visible;
        opacity: 1;
    }
    </style>
    """, unsafe_allow_html=True)
    
    return

# Commonly used UI components
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
    else:
        st.info(content)

def render_card(title, content, icon=None, is_expanded=False):
    """
    Render a card with expandable content
    
    Args:
        title (str): Card title
        content (str): Card content (markdown)
        icon (str): Optional icon
        is_expanded (bool): Whether the card is expanded by default
    """
    if icon:
        title = f"{icon} {title}"
    
    with st.expander(title, expanded=is_expanded):
        st.markdown(content)

def initialize_session():
    """Initialize common session state variables"""
    if "user_id" not in st.session_state:
        st.session_state.user_id = "anonymous_user"
    
    if "theme" not in st.session_state:
        st.session_state.theme = "light"
    
    if "sidebar_state" not in st.session_state:
        st.session_state.sidebar_state = "expanded"

# Call setup_page_config at module import time
setup_page_config() 