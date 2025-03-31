"""
Reusable UI components for the Resume AI application
"""

import streamlit as st

def loading_spinner(text="Please wait..."):
    """
    Display a loading spinner with custom text
    
    Args:
        text (str): Text to display with the spinner
    
    Returns:
        st.empty: Container to use with spinner context manager
    """
    return st.spinner(text)

def progress_bar(text="Progress"):
    """
    Create a progress bar with text
    
    Args:
        text (str): Label for the progress bar
    
    Returns:
        tuple: (progress_bar, status_text) where progress_bar is the streamlit progress bar
              and status_text is an empty container for status text
    """
    class ProgressContainer:
        def __init__(self, progress_bar, status_text):
            self.progress_bar = progress_bar
            self.status_text = status_text
            
        def progress(self, percent, text=None):
            """Update progress bar and optionally the status text"""
            self.progress_bar.progress(percent)
            if text:
                self.status_text.text(text)
    
    status_text = st.empty()
    status_text.text(text)
    progress_bar = st.progress(0)
    
    return ProgressContainer(progress_bar, status_text)

def sidebar_info(content, icon="ℹ️"):
    """
    Display information in the sidebar
    
    Args:
        content (str): Markdown content to display
        icon (str): Icon to display before the content
    """
    with st.sidebar:
        st.markdown(f"{icon} {content}")

def feature_card(title, description, icon, on_click=None):
    """
    Display a feature card
    
    Args:
        title (str): Card title
        description (str): Card description
        icon (str): Icon to display
        on_click (function): Function to call when card is clicked
    """
    # Create a container for the card with a border
    card_html = f"""
    <div style="border: 1px solid #ddd; border-radius: 5px; padding: 15px; margin-bottom: 10px; cursor: pointer;">
        <div style="font-size: 2em; margin-bottom: 10px;">{icon}</div>
        <h3>{title}</h3>
        <p>{description}</p>
    </div>
    """
    
    st.markdown(card_html, unsafe_allow_html=True)
    
    # Add a button for the click action
    if on_click:
        if st.button(f"Try {title}", key=f"btn_{title}"):
            on_click()

def testimonial_card(quote, author, rating=5):
    """
    Display a testimonial card
    
    Args:
        quote (str): The testimonial text
        author (str): The author of the testimonial
        rating (int): Rating out of 5
    """
    stars = "⭐" * rating
    
    card_html = f"""
    <div style="border: 1px solid #ddd; border-radius: 5px; padding: 15px; margin: 10px 0; background-color: #f9f9f9;">
        <p style="font-style: italic;">"{quote}"</p>
        <p style="text-align: right;">— {author}</p>
        <div style="text-align: right; color: #FFD700;">{stars}</div>
    </div>
    """
    
    st.markdown(card_html, unsafe_allow_html=True)

def section_header(title, description=None, icon=None):
    """
    Display a section header with optional description and icon
    
    Args:
        title (str): Section title
        description (str): Optional description
        icon (str): Optional icon
    """
    if icon:
        title = f"{icon} {title}"
    
    st.markdown(f"## {title}")
    
    if description:
        st.markdown(f"*{description}*")

def info_card(content, box_type="info"):
    """
    Display an info card
    
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