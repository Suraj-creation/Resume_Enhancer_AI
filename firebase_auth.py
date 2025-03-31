import firebase_admin
from firebase_admin import credentials, auth
import json
import os
import streamlit as st
from utils.api_config import API_CONFIG

class FirebaseAuthClient:
    def __init__(self):
        self.firebase_config = API_CONFIG["firebase"]
        self.initialized = False
        self.initialize_firebase()
        
    def initialize_firebase(self):
        """Initialize Firebase Admin SDK with credentials"""
        try:
            # Check if already initialized
            if self.initialized or firebase_admin._apps:
                self.initialized = True
                return
            
            # Get Firebase credentials from config
            if not all([self.firebase_config["api_key"], 
                       self.firebase_config["auth_domain"], 
                       self.firebase_config["project_id"]]):
                st.warning("Firebase credentials are not fully configured. Authentication will be simulated.")
                return
            
            # Create a credential file if not exists
            cred_path = "firebase-credentials.json"
            if not os.path.exists(cred_path):
                # Create a minimal credentials file for Firebase Admin
                cred_data = {
                    "type": "service_account",
                    "project_id": self.firebase_config["project_id"],
                    "private_key_id": "simulated",
                    "private_key": "-----BEGIN PRIVATE KEY-----\nsimulated\n-----END PRIVATE KEY-----\n",
                    "client_email": f"firebase-adminsdk@{self.firebase_config['project_id']}.iam.gserviceaccount.com",
                    "client_id": "simulated",
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                    "client_x509_cert_url": f"https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk%40{self.firebase_config['project_id']}.iam.gserviceaccount.com"
                }
                
                with open(cred_path, 'w') as f:
                    json.dump(cred_data, f)
            
            # Initialize Firebase Admin SDK
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
            self.initialized = True
            
        except Exception as e:
            st.warning(f"Firebase initialization error: {str(e)}. Authentication will be simulated.")
    
    def login(self, email, password):
        """
        Authenticate a user with email and password
        
        Args:
            email: User's email
            password: User's password
            
        Returns:
            dict: User data if successful, None if failed
        """
        if not self.initialized:
            # Simulate authentication for demo purposes
            if email and password:
                return {
                    "uid": "simulated_uid",
                    "email": email,
                    "name": email.split("@")[0],
                    "is_simulated": True
                }
            return None
        
        try:
            # In a real implementation, you would use Firebase Auth REST API
            # to verify password and get user info
            # This is a simplified example
            user = auth.get_user_by_email(email)
            return {
                "uid": user.uid,
                "email": user.email,
                "name": user.display_name or email.split("@")[0],
                "is_simulated": False
            }
        except Exception as e:
            st.error(f"Login error: {str(e)}")
            return None
    
    def register(self, name, email, password):
        """
        Register a new user
        
        Args:
            name: User's name
            email: User's email
            password: User's password
            
        Returns:
            dict: User data if successful, None if failed
        """
        if not self.initialized:
            # Simulate registration for demo purposes
            if name and email and password:
                return {
                    "uid": "simulated_uid",
                    "email": email,
                    "name": name,
                    "is_simulated": True
                }
            return None
        
        try:
            # Create the user
            user = auth.create_user(
                email=email,
                password=password,
                display_name=name
            )
            
            return {
                "uid": user.uid,
                "email": user.email,
                "name": user.display_name,
                "is_simulated": False
            }
        except Exception as e:
            st.error(f"Registration error: {str(e)}")
            return None
    
    def reset_password(self, email):
        """
        Send password reset email
        
        Args:
            email: User's email
            
        Returns:
            bool: True if email sent, False otherwise
        """
        if not self.initialized:
            # Simulate password reset for demo purposes
            return True
        
        try:
            # In a real implementation, you would use Firebase Auth REST API
            # to send password reset email
            # This is a simplified example
            link = auth.generate_password_reset_link(email)
            # In a real app, you would send this link via email
            return True
        except Exception as e:
            st.error(f"Password reset error: {str(e)}")
            return False
    
    def logout(self):
        """
        Log out the current user
        
        Returns:
            bool: True if successful
        """
        # In a Streamlit app, logout is handled by clearing session state
        return True

# Initialize Firebase Auth client
firebase_auth = FirebaseAuthClient() 