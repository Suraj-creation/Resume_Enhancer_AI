import os
from dotenv import load_dotenv
import streamlit as st

# Load environment variables
load_dotenv()

class SupabaseClient:
    """
    A class to manage Supabase authentication and data access
    """
    
    def __init__(self):
        """Initialize the Supabase client using environment variables"""
        self.supabase_url = os.environ.get("SUPABASE_URL", "")
        self.supabase_key = os.environ.get("SUPABASE_KEY", "")
        
        # In a real implementation, we would use the official Supabase client
        # For this demo, we'll simulate authentication
        self.is_connected = bool(self.supabase_url and self.supabase_key)
    
    def sign_up(self, email, password, metadata=None):
        """
        Register a new user
        
        Parameters:
        - email: User's email
        - password: User's password
        - metadata: Optional additional user data
        
        Returns:
        - Success flag and user data or error message
        """
        # In a real implementation, call Supabase API
        # For demo, we'll simulate success
        
        if not self.is_connected:
            return False, "Supabase configuration missing"
        
        if not email or not password:
            return False, "Email and password are required"
        
        if "@" not in email or len(password) < 6:
            return False, "Invalid email or password too short"
        
        # Simulate successful registration
        user_data = {
            "id": "simulated-user-id",
            "email": email,
            "metadata": metadata or {}
        }
        
        return True, user_data
    
    def sign_in(self, email, password):
        """
        Authenticate a user
        
        Parameters:
        - email: User's email
        - password: User's password
        
        Returns:
        - Success flag and user data or error message
        """
        # In a real implementation, call Supabase API
        # For demo, we'll simulate success
        
        if not self.is_connected:
            return False, "Supabase configuration missing"
        
        # Check for empty or None values and convert to empty strings if needed
        email = "" if email is None else email.strip()
        password = "" if password is None else password
        
        if not email or not password:
            return False, "Email and password are required"
        
        # Simulate successful login
        user_data = {
            "id": "simulated-user-id",
            "email": email,
            "name": email.split("@")[0]
        }
        
        return True, user_data
    
    def sign_out(self):
        """
        Sign out the current user
        
        Returns:
        - Success flag
        """
        # In a real implementation, call Supabase API
        # For demo, simply return success
        return True
    
    def get_user(self, user_id):
        """
        Get user data by ID
        
        Parameters:
        - user_id: The user's ID
        
        Returns:
        - User data or None
        """
        # In a real implementation, fetch from Supabase
        # For demo, return simulated data
        if not user_id:
            return None
        
        return {
            "id": user_id,
            "email": "user@example.com",
            "name": "Demo User"
        }
    
    def save_resume(self, user_id, resume_data):
        """
        Save a resume for a user
        
        Parameters:
        - user_id: The user's ID
        - resume_data: Dictionary with resume information
        
        Returns:
        - Success flag and resume ID or error
        """
        # In a real implementation, store in Supabase
        # For demo, return success
        if not user_id or not resume_data:
            return False, "Missing user ID or resume data"
        
        return True, "simulated-resume-id"
    
    def get_user_resumes(self, user_id):
        """
        Get all resumes for a user
        
        Parameters:
        - user_id: The user's ID
        
        Returns:
        - List of resume data
        """
        # In a real implementation, fetch from Supabase
        # For demo, return empty list
        if not user_id:
            return []
        
        # For demo purposes, return a simulated resume
        return [{
            "id": "simulated-resume-id",
            "name": "My Resume",
            "created_at": "2023-08-15",
            "last_updated": "2023-08-15"
        }]

# Initialize a global Supabase client instance
_supabase_client = None

def get_supabase_client():
    """
    Returns a singleton instance of the SupabaseClient
    
    Returns:
        SupabaseClient: The initialized Supabase client
    """
    global _supabase_client
    if _supabase_client is None:
        _supabase_client = SupabaseClient()
    return _supabase_client

def initialize_supabase():
    """
    Initialize and return the Supabase client
    
    Returns:
        SupabaseClient: The initialized Supabase client
    """
    return get_supabase_client() 