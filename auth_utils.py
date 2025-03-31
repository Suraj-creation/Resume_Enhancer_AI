import streamlit as st
from utils.supabase_client import get_supabase_client

def initialize_auth():
    """Initialize authentication system"""
    return get_supabase_client()

def require_auth(db=None):
    """Check if user is authenticated, if not, show login/signup form
    
    Returns:
        dict: User information if authenticated, None otherwise
    """
    # Check if user is already authenticated in session state
    if st.session_state.get('authenticated', False) and st.session_state.get('user_id'):
        # Return user info in the same format expected by the app
        return {
            "id": st.session_state.get('user_id'),
            "email": st.session_state.get('user_email'),
            "name": st.session_state.get('user_name')
        }
    
    # Get Supabase client
    supabase = get_supabase_client()
    
    # If not authenticated, redirect to the main page which handles auth
    st.error("You need to sign in to access this feature.")
    st.session_state.page = "home"  # Redirect to home page for authentication
    st.session_state.auth_page = "login"  # Show login page
    st.rerun()
    
    return None

def logout():
    """Log out the current user"""
    # Use Supabase to sign out
    supabase = get_supabase_client()
    success = supabase.sign_out()
    
    # Clear authentication state
    st.session_state.authenticated = False
    st.session_state.user_id = None
    st.session_state.user_email = None
    st.session_state.user_name = None
    
    # Keep the page state but set to home
    st.session_state.page = "home"
    
    # Clear other sensitive session state variables
    keys_to_clear = [key for key in st.session_state.keys() 
                     if key not in ['page', 'authenticated', 'user_id', 'user_email', 'user_name']]
    for key in keys_to_clear:
        del st.session_state[key]
            
    st.rerun()

def get_current_user():
    """Get the current authenticated user
    
    Returns:
        dict: User information if authenticated, None otherwise
    """
    if st.session_state.get('authenticated', False) and st.session_state.get('user_id'):
        return {
            "id": st.session_state.get('user_id'),
            "email": st.session_state.get('user_email'),
            "name": st.session_state.get('user_name')
        }
    return None 