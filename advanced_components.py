import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import base64
from streamlit.components.v1 import html
import time
from datetime import datetime
import numpy as np
import json

def load_advanced_css():
    """
    Load advanced CSS with animations, transitions, and modern design elements
    """
    st.markdown("""
    <style>
        /* Advanced color scheme with CSS variables */
        :root {
            --primary-color: #4361EE;
            --primary-light: #4CC9F0;
            --primary-dark: #3A0CA3;
            --secondary-color: #7209B7;
            --accent-color: #F72585;
            --success-color: #4CAF50;
            --warning-color: #FF9800;
            --danger-color: #F44336;
            --background-color: #F8F9FA;
            --card-bg-color: #FFFFFF;
            --text-color: #212529;
            --text-muted: #6C757D;
            --border-radius: 8px;
            --box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            --transition-speed: 0.3s;
        }

        /* Dark mode support (Streamlit has a built-in dark mode) */
        @media (prefers-color-scheme: dark) {
            :root {
                --background-color: #121212;
                --card-bg-color: #1E1E1E;
                --text-color: #E0E0E0;
                --text-muted: #AAAAAA;
            }
        }
        
        /* Global typography */
        body {
            font-family: 'Roboto', sans-serif;
            color: var(--text-color);
            background-color: var(--background-color);
        }
        
        h1, h2, h3, h4, h5, h6 {
            font-weight: 600;
            color: var(--primary-color);
        }
        
        /* Custom card with hover effects */
        .custom-card {
            background-color: var(--card-bg-color);
            border-radius: var(--border-radius);
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            box-shadow: var(--box-shadow);
            transition: transform var(--transition-speed), box-shadow var(--transition-speed);
            border-left: 3px solid var(--primary-color);
        }
        
        .custom-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 20px rgba(0, 0, 0, 0.12);
        }
        
        /* Animated buttons with hover effect */
        .stButton > button {
            background-color: var(--primary-color);
            color: white;
            border-radius: var(--border-radius);
            border: none;
            padding: 0.5rem 1rem;
            font-weight: 500;
            transition: all var(--transition-speed);
            position: relative;
            overflow: hidden;
        }
        
        .stButton > button:hover {
            background-color: var(--primary-dark);
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        }
        
        .stButton > button:active {
            transform: translateY(0);
        }
        
        /* Ripple effect for buttons */
        .stButton > button::after {
            content: '';
            position: absolute;
            top: 50%;
            left: 50%;
            width: 5px;
            height: 5px;
            background: rgba(255, 255, 255, 0.5);
            opacity: 0;
            border-radius: 100%;
            transform: scale(1, 1) translate(-50%);
            transform-origin: 50% 50%;
        }
        
        .stButton > button:focus:not(:active)::after {
            animation: ripple 1s ease-out;
        }
        
        @keyframes ripple {
            0% {
                transform: scale(0, 0);
                opacity: 0.5;
            }
            20% {
                transform: scale(25, 25);
                opacity: 0.3;
            }
            100% {
                opacity: 0;
                transform: scale(40, 40);
            }
        }
        
        /* Enhanced score container */
        .score-container {
            padding: 1.5rem;
            border-radius: var(--border-radius);
            margin-bottom: 1.5rem;
            text-align: center;
            transition: all var(--transition-speed);
            position: relative;
            overflow: hidden;
        }
        
        .score-container:hover {
            transform: scale(1.02);
        }
        
        .high-score {
            background: linear-gradient(135deg, rgba(76, 175, 80, 0.1) 0%, rgba(76, 175, 80, 0.2) 100%);
            border: 1px solid var(--success-color);
        }
        
        .medium-score {
            background: linear-gradient(135deg, rgba(255, 152, 0, 0.1) 0%, rgba(255, 152, 0, 0.2) 100%);
            border: 1px solid var(--warning-color);
        }
        
        .low-score {
            background: linear-gradient(135deg, rgba(244, 67, 54, 0.1) 0%, rgba(244, 67, 54, 0.2) 100%);
            border: 1px solid var(--danger-color);
        }
        
        /* Circular score indicator */
        .score-circle {
            width: 120px;
            height: 120px;
            border-radius: 50%;
            margin: 0 auto 1rem auto;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 2rem;
            font-weight: 700;
            color: white;
            position: relative;
            overflow: hidden;
            background: conic-gradient(var(--primary-color) 0%, var(--primary-color) calc(var(--score) * 1%), #e0e0e0 calc(var(--score) * 1%), #e0e0e0 100%);
        }
        
        .score-circle::before {
            content: '';
            position: absolute;
            top: 10px;
            left: 10px;
            right: 10px;
            bottom: 10px;
            background: var(--card-bg-color);
            border-radius: 50%;
            z-index: 1;
        }
        
        .score-circle-content {
            position: relative;
            z-index: 2;
            color: var(--text-color);
        }
        
        /* Enhanced progress bar for steps */
        .step-progress {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 2rem;
            position: relative;
        }
        
        .step-progress::before {
            content: '';
            position: absolute;
            top: 50%;
            left: 0;
            right: 0;
            height: 2px;
            background-color: #e0e0e0;
            transform: translateY(-50%);
            z-index: 1;
        }
        
        .step-item {
            width: 30px;
            height: 30px;
            border-radius: 50%;
            background-color: white;
            border: 2px solid #e0e0e0;
            z-index: 2;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 600;
            font-size: 14px;
            color: #6c757d;
            transition: all var(--transition-speed);
            position: relative;
        }
        
        .step-item.active {
            background-color: var(--primary-color);
            border-color: var(--primary-color);
            color: white;
        }
        
        .step-item.completed {
            background-color: var(--success-color);
            border-color: var(--success-color);
            color: white;
        }
        
        .step-item::after {
            content: attr(data-label);
            position: absolute;
            top: 40px;
            left: 50%;
            transform: translateX(-50%);
            white-space: nowrap;
            font-size: 12px;
            font-weight: 500;
            color: var(--text-muted);
        }
        
        /* File uploader styling */
        .uploadedFile {
            border: 2px dashed #ccc;
            border-radius: var(--border-radius);
            padding: 2rem 1rem;
            text-align: center;
            margin-bottom: 1rem;
            transition: all var(--transition-speed);
        }
        
        .uploadedFile:hover {
            border-color: var(--primary-color);
        }
        
        /* Enhanced tabs */
        .stTabs [role="tablist"] {
            border-bottom: 1px solid rgba(0, 0, 0, 0.1);
        }
        
        .stTabs [role="tab"] {
            padding: 0.5rem 1rem;
            margin-right: 0.25rem;
            border-radius: var(--border-radius) var(--border-radius) 0 0;
            transition: all var(--transition-speed);
        }
        
        .stTabs [role="tab"][aria-selected="true"] {
            background-color: var(--primary-color);
            color: white;
        }
        
        /* Tooltip styles */
        .tooltip {
            position: relative;
            display: inline-block;
            cursor: help;
        }
        
        .tooltip .tooltip-text {
            visibility: hidden;
            width: 200px;
            background-color: #333;
            color: #fff;
            text-align: center;
            border-radius: 6px;
            padding: 0.5rem;
            position: absolute;
            z-index: 1;
            bottom: 125%;
            left: 50%;
            margin-left: -100px;
            opacity: 0;
            transition: opacity var(--transition-speed);
        }
        
        .tooltip:hover .tooltip-text {
            visibility: visible;
            opacity: 1;
        }
        
        /* Animation for loading */
        @keyframes pulse {
            0% { opacity: 0.6; }
            50% { opacity: 1; }
            100% { opacity: 0.6; }
        }
        
        .loading {
            animation: pulse 1.5s infinite ease-in-out;
        }
        
        /* Section animations */
        .fade-in {
            animation: fadeIn 0.5s ease-in-out;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        /* Comparison container for before/after */
        .comparison-container {
            display: flex;
            gap: 1rem;
        }
        
        .comparison-side {
            flex: 1;
            padding: 1rem;
            border-radius: var(--border-radius);
            background-color: var(--card-bg-color);
            box-shadow: var(--box-shadow);
        }
        
        .comparison-side.original {
            border-left: 3px solid var(--warning-color);
        }
        
        .comparison-side.enhanced {
            border-left: 3px solid var(--success-color);
        }
        
        /* Template selection styling */
        .template-card {
            border-radius: var(--border-radius);
            padding: 1.5rem;
            text-align: center;
            background-color: var(--card-bg-color);
            box-shadow: var(--box-shadow);
            cursor: pointer;
            transition: all var(--transition-speed);
            border: 2px solid transparent;
        }
        
        .template-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 20px rgba(0, 0, 0, 0.12);
        }
        
        .template-card.selected {
            border-color: var(--primary-color);
        }
        
        /* Custom slider for score display */
        .score-slider-container {
            width: 100%;
            height: 20px;
            background-color: #e0e0e0;
            border-radius: 10px;
            overflow: hidden;
            margin: 1rem 0;
            position: relative;
        }
        
        .score-slider-fill {
            height: 100%;
            background: linear-gradient(90deg, var(--danger-color) 0%, var(--warning-color) 50%, var(--success-color) 100%);
            border-radius: 10px;
            width: var(--score-percent);
            transition: width 1s ease-in-out;
        }
        
        .score-slider-marker {
            position: absolute;
            width: 2px;
            height: 30px;
            background-color: var(--text-color);
            top: -5px;
            left: calc(var(--score-percent) - 1px);
            z-index: 2;
        }
        
        /* Tooltip for score explanation */
        .score-explanation {
            margin-top: 0.5rem;
            font-size: 0.85rem;
            color: var(--text-muted);
            font-style: italic;
        }
        
        /* Quick navigation floating button */
        .floating-nav {
            position: fixed;
            bottom: 2rem;
            right: 2rem;
            width: 60px;
            height: 60px;
            border-radius: 50%;
            background-color: var(--primary-color);
            color: white;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
            cursor: pointer;
            z-index: 1000;
            transition: all var(--transition-speed);
        }
        
        .floating-nav:hover {
            transform: scale(1.1);
        }
        
        .floating-nav-menu {
            position: absolute;
            bottom: 70px;
            right: 0;
            background-color: var(--card-bg-color);
            border-radius: var(--border-radius);
            box-shadow: var(--box-shadow);
            padding: 0.5rem;
            width: 200px;
            display: none;
        }
        
        .floating-nav:hover .floating-nav-menu {
            display: block;
        }
        
        .floating-nav-item {
            padding: 0.5rem 1rem;
            cursor: pointer;
            transition: all var(--transition-speed);
            border-radius: 4px;
        }
        
        .floating-nav-item:hover {
            background-color: rgba(0, 0, 0, 0.05);
            color: var(--primary-color);
        }
    </style>
    """, unsafe_allow_html=True)

def render_step_progress(current_step, total_steps, step_labels=None):
    """Render a custom step progress indicator"""
    if step_labels is None:
        step_labels = [f"Step {i+1}" for i in range(total_steps)]
    
    st.markdown("""
    <style>
    .step-progress {
        display: flex;
        justify-content: space-between;
        margin: 2rem 0;
        position: relative;
    }
    .step-marker {
        width: 30px;
        height: 30px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        z-index: 2;
    }
    .step-label {
        position: absolute;
        top: 35px;
        text-align: center;
        font-size: 0.8rem;
        width: 100px;
        transform: translateX(-35px);
    }
    .step-line {
        position: absolute;
        top: 15px;
        height: 2px;
        z-index: 1;
    }
    </style>
    """, unsafe_allow_html=True)
    
    progress_html = '<div class="step-progress">'
    
    for i in range(total_steps):
        if i < current_step:
            # Completed step
            marker_style = "background-color: #4361EE; color: white;"
            label_style = "color: #4361EE; font-weight: 500;"
        elif i == current_step:
            # Current step
            marker_style = "background-color: white; color: #4361EE; border: 2px solid #4361EE;"
            label_style = "color: #4361EE; font-weight: 600;"
        else:
            # Future step
            marker_style = "background-color: #f1f5f9; color: #94a3b8;"
            label_style = "color: #94a3b8;"
        
        # Calculate position
        position = f"left: {i * (100 / (total_steps - 1))}%;" if total_steps > 1 else "left: 0;"
        
        # Add step marker and label
        progress_html += f"""
        <div class="step-marker" style="{marker_style} {position}">{i + 1}</div>
        <div class="step-label" style="{label_style} {position}">{step_labels[i]}</div>
        """
    
    # Add connector lines between steps
    for i in range(total_steps - 1):
        width = 100 / (total_steps - 1)
        position = f"left: {i * width}%;"
        line_width = f"width: {width}%;"
        
        if i < current_step:
            # Line for completed steps
            line_style = "background-color: #4361EE;"
    else:
            # Line for upcoming steps
            line_style = "background-color: #f1f5f9;"
        
        progress_html += f'<div class="step-line" style="{line_style} {position} {line_width}"></div>'
    
    progress_html += '</div>'
    
    st.markdown(progress_html, unsafe_allow_html=True)

def render_score_circle(score, max_score=100, label="Match Score"):
    """Render a circular score indicator"""
    percentage = (score / max_score) * 100
    
    # Determine color based on score
    if percentage >= 80:
        color = "#10B981"  # Green
    elif percentage >= 60:
        color = "#FBBF24"  # Yellow
    else:
        color = "#EF4444"  # Red
    
    html = f"""
    <div style="display: flex; flex-direction: column; align-items: center; margin: 1rem 0;">
        <div style="position: relative; width: 120px; height: 120px;">
            <svg viewBox="0 0 36 36" style="width: 100%; height: 100%;">
                <path d="M18 2.0845
                    a 15.9155 15.9155 0 0 1 0 31.831
                    a 15.9155 15.9155 0 0 1 0 -31.831"
                    fill="none" stroke="#E5E7EB" stroke-width="3" stroke-dasharray="100, 100"/>
                <path d="M18 2.0845
                    a 15.9155 15.9155 0 0 1 0 31.831
                    a 15.9155 15.9155 0 0 1 0 -31.831"
                    fill="none" stroke="{color}" stroke-width="3" stroke-dasharray="{percentage}, 100"/>
            </svg>
            <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); text-align: center;">
                <div style="font-size: 1.8rem; font-weight: 700; color: {color};">{score}</div>
                <div style="font-size: 0.8rem; color: #6B7280;">/{max_score}</div>
        </div>
        </div>
        <div style="font-size: 1rem; font-weight: 500; color: #1F2937; margin-top: 0.5rem;">{label}</div>
    </div>
    """
    
    st.markdown(html, unsafe_allow_html=True)

def render_section_comparison(original, enhanced, section_name):
    """Render a side-by-side comparison of original and enhanced content"""
    # Implementation can be added later
    pass

def render_template_selection(templates, current_selection=None):
    """Render a grid of selectable resume templates"""
    # Implementation can be added later
    pass

def render_animated_score_slider(score, max_score=100, title="Score", description=None):
    """Render an animated horizontal score slider"""
    percentage = (score / max_score) * 100
    
    # Determine color based on score
    if percentage >= 80:
        color = "#10B981"  # Green
        emoji = "🚀"
        message = "Excellent"
    elif percentage >= 60:
        color = "#FBBF24"  # Yellow
        emoji = "👍"
        message = "Good"
    else:
        color = "#EF4444"  # Red
        emoji = "⚠️"
        message = "Needs Improvement"
    
    html = f"""
    <div style="margin: 1rem 0; padding: 1rem; background-color: white; border-radius: 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
            <h4 style="margin: 0; font-size: 1.1rem; color: #1F2937;">{title}</h4>
            <div style="display: flex; align-items: center;">
                <span style="font-size: 1.2rem; margin-right: 0.25rem;">{emoji}</span>
                <span style="font-weight: 600; color: {color};">{message}</span>
        </div>
    </div>
        
        <div style="position: relative; height: 12px; background-color: #F3F4F6; border-radius: 9999px; overflow: hidden; margin: 0.75rem 0;">
            <div style="position: absolute; height: 100%; width: {percentage}%; background-color: {color}; border-radius: 9999px;"></div>
        </div>
        
        <div style="display: flex; justify-content: space-between; font-size: 0.85rem; color: #6B7280;">
            <div>0</div>
            <div style="font-weight: 600; color: {color};">{score}/{max_score}</div>
            <div>{max_score}</div>
            </div>
    
        {f'<p style="margin: 0.5rem 0 0 0; font-size: 0.9rem; color: #4B5563;">{description}</p>' if description else ''}
    </div>
    """
    
    st.markdown(html, unsafe_allow_html=True)

def create_radar_chart(categories, values, title="Skills Assessment"):
    """Create a radar chart for skills visualization"""
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        fillcolor='rgba(67, 97, 238, 0.2)',
        line=dict(color='#4361EE', width=2),
        name="Skills"
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 10]
            )
        ),
        showlegend=False,
        title=dict(
            text=title,
            x=0.5,
            font=dict(
                family="Inter, sans-serif",
                size=18,
                color="#1F2937"
            )
        ),
        margin=dict(l=50, r=50, t=70, b=50),
        height=400
    )
    
    return fig

def render_tooltip(text, tooltip_content):
    """Render text with a tooltip on hover"""
    st.markdown(f"""
    <div class="tooltip">
        {text} <span style="font-size: 1rem; cursor: pointer;">ℹ️</span>
        <span class="tooltiptext">{tooltip_content}</span>
    </div>
    """, unsafe_allow_html=True)

def animate_text_analysis(message, analysis_time=3):
    """Show an animated text analysis message"""
    # Implementation can be added later
    pass

def render_custom_card(title, content, icon=None):
    """Render a custom styled card"""
    # Implementation can be added later
    pass

def floating_help_button(tooltip_text="Need help?"):
    """Render a floating help button with tooltip"""
    st.markdown(f"""
    <div style="position: fixed; bottom: 20px; right: 20px; z-index: 1000;">
        <div class="tooltip">
            <button style="background-color: #4361EE; color: white; border: none; width: 48px; height: 48px; 
                        border-radius: 50%; font-size: 1.5rem; cursor: pointer; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
                ?
            </button>
            <span class="tooltiptext" style="width: 200px; bottom: 150%; left: 50%; margin-left: -100px;">
                {tooltip_text}
            </span>
            </div>
        </div>
    """, unsafe_allow_html=True)

def display_info_card(title, content, icon_emoji="ℹ️"):
    """
    Display an informational card with icon
    
    Args:
        title: Card title
        content: Card content 
        icon_emoji: Emoji for icon
    """
    st.markdown(f"""
    <div style="padding: 1rem; background-color: #f8f9fa; border-radius: 0.5rem; 
                margin: 1rem 0; border-left: 4px solid #4361EE;">
        <div style="font-size: 1.1rem; font-weight: 600; margin-bottom: 0.5rem; 
                   display: flex; align-items: center;">
            <span style="margin-right: 0.5rem; font-size: 1.4rem;">{icon_emoji}</span>
            {title}
        </div>
        <div>{content}</div>
    </div>
    """, unsafe_allow_html=True)

def render_sidebar(authenticated=False, user=None):
    """
    Render the sidebar with navigation and user info
    
    Args:
        authenticated: Whether the user is authenticated
        user: User information dict
    """
    with st.sidebar:
        st.image("https://img.icons8.com/fluency/96/000000/document-certificate.png", width=40)
        st.markdown("<h1 style='font-size: 1.5rem; margin-top: -0.5rem;'>Resume AI</h1>", unsafe_allow_html=True)
        
        st.markdown("<hr style='margin: 1rem 0;'>", unsafe_allow_html=True)
        
        if authenticated and user:
            # User profile section
            st.markdown(f"""
            <div style="padding: 0.5rem; background-color: #f8f9fa; border-radius: 0.5rem; 
                        margin-bottom: 1rem;">
                <div style="font-weight: 600; font-size: 1.1rem;">Welcome!</div>
                <div style="color: #555; font-size: 0.9rem;">{user.get('email', 'User')}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Navigation
            st.markdown("### Navigation")
            
            # Active page highlighting
            current_page = st.session_state.get("current_page", "Home")
            
            for page, icon in [
                ("Home", "🏠"),
                ("Resume Enhancer", "✨"),
                ("Resume Job Matching", "🔍"),
                ("History", "📋"),
                ("Settings", "⚙️")
            ]:
                active = page == current_page
                bg_color = "#e8f0fe" if active else "transparent"
                color = "#1a73e8" if active else "#333"
                
                if st.sidebar.button(
                    f"{icon} {page}", 
                    key=f"nav_{page}",
                    help=f"Navigate to {page}"
                ):
                    st.session_state.current_page = page
                    # In a real multi-page app, would redirect to the page
                    st.rerun()
            
            # Logout at bottom
            st.markdown("<hr style='margin: 1rem 0;'>", unsafe_allow_html=True)
            if st.sidebar.button("🚪 Logout", key="logout"):
                # Clear session state and log out
                st.session_state.authenticated = False
                st.session_state.user = None
                st.rerun()
                
        else:
            # For unauthenticated users, show minimal sidebar
            st.markdown("""
            ### Get Started
            Login or create an account to start using Resume AI.
            """)
        
        # Always show app version at bottom
        st.markdown("""
        <div style="position: fixed; bottom: 0; left: 0; padding: 1rem; 
                   font-size: 0.8rem; color: #666; width: 100%; text-align: center;">
            Resume AI v1.0.0
        </div>
        """, unsafe_allow_html=True) 