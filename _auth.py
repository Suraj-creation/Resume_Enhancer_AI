"""
Bridge file to redirect to authentication utilities
"""
from utils.auth_ui import (
    is_valid_email,
    check_authentication,
    render_login_ui,
    render_signup_ui,
    login,
    signup,
    logout
)

# Re-export all functionality from auth_ui.py
__all__ = [
    'is_valid_email',
    'check_authentication',
    'render_login_ui', 
    'render_signup_ui',
    'login',
    'signup',
    'logout'
] 