import streamlit as st
import re
from utils.supabase_client import get_supabase_client

# Initialize Supabase client
supabase = get_supabase_client()

def is_valid_email(email):
    """Validates email format using regex"""
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None

def check_authentication():
    """Check if the user is authenticated"""
    return st.session_state.get('authenticated', False)

def render_login_ui():
    """Render the login UI with enhanced styling"""
    
    # Add debugging for session state initialization
    if 'login_email' not in st.session_state:
        st.session_state.login_email = ""
    if 'login_password' not in st.session_state:
        st.session_state.login_password = ""
    
    st.markdown("""
    <div style="max-width: 450px; margin: 0 auto; padding: 2rem; background-color: white; 
                border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
        <h2 style="text-align: center; margin-bottom: 1.5rem; color: #333;">Sign In</h2>
    """, unsafe_allow_html=True)
    
    with st.form("login_form"):
        email_input = st.text_input("Email", key="login_email_input", 
                     placeholder="Enter your email address")
        password_input = st.text_input("Password", type="password", key="login_password_input",
                     placeholder="Enter your password")
        
        col1, col2 = st.columns([1, 1])
        with col1:
            submit = st.form_submit_button("Login", use_container_width=True)
        with col2:
            demo_button = st.form_submit_button("Try Demo", use_container_width=True)
        
        # Remember me and forgot password
        col3, col4 = st.columns([1, 1])
        with col3:
            remember = st.checkbox("Remember me", value=True)
        with col4:
            st.markdown("<div style='text-align: right;'><a href='#' style='color: #4361EE; text-decoration: none; font-size: 0.9rem;'>Forgot password?</a></div>", unsafe_allow_html=True)
        
        if submit:
            # Update session state with form values
            st.session_state.login_email = email_input
            st.session_state.login_password = password_input
            # Add debugging before login attempt
            st.write(f"Form submitted. Email: '{st.session_state.login_email}', Password length: {len(st.session_state.login_password) if st.session_state.login_password else 0}")
            login(st.session_state.login_email, st.session_state.login_password)
        
        if demo_button:
            # Update session state with demo credentials
            st.session_state.login_email = "demo@example.com"
            st.session_state.login_password = "demo123"
            # Add debugging for demo login
            st.write(f"Demo login. Email: '{st.session_state.login_email}', Password length: {len(st.session_state.login_password)}")
            login(st.session_state.login_email, st.session_state.login_password, is_demo=True)
    
    # Social login options
    st.markdown("""
    <div style="text-align: center; margin-top: 1rem;">
        <p style="font-size: 0.9rem; color: #666; margin-bottom: 0.5rem;">Or continue with</p>
        <div style="display: flex; justify-content: center; gap: 1rem;">
            <a href="#" style="text-decoration: none;">
                <img src="https://img.icons8.com/color/48/000000/google-logo.png" width="30">
            </a>
            <a href="#" style="text-decoration: none;">
                <img src="https://img.icons8.com/color/48/000000/linkedin.png" width="30">
            </a>
            <a href="#" style="text-decoration: none;">
                <img src="https://img.icons8.com/color/48/000000/github.png" width="30">
            </a>
        </div>
    </div>
    </div>
    """, unsafe_allow_html=True)

def render_signup_ui():
    """Render the signup UI with enhanced styling"""
    
    st.markdown("""
    <div style="max-width: 450px; margin: 0 auto; padding: 2rem; background-color: white; 
                border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
        <h2 style="text-align: center; margin-bottom: 1.5rem; color: #333;">Create Account</h2>
    """, unsafe_allow_html=True)
    
    with st.form("signup_form"):
        st.text_input("Full Name", key="signup_name", 
                     placeholder="Enter your full name")
        st.text_input("Email", key="signup_email", 
                     placeholder="Enter your email address")
        st.text_input("Password", type="password", key="signup_password",
                     placeholder="Create a password (min. 6 characters)")
        st.text_input("Confirm Password", type="password", key="signup_password_confirm",
                     placeholder="Confirm your password")
        
        terms_agree = st.checkbox("I agree to the Terms of Service and Privacy Policy")
        
        submit = st.form_submit_button("Create Account", use_container_width=True)
        
        if submit:
            signup()
    
    # Alternative options
    st.markdown("""
    <div style="text-align: center; margin-top: 1rem;">
        <p style="font-size: 0.9rem; color: #666;">Already have an account? <a href="#" style="color: #4361EE; text-decoration: none;">Sign in</a></p>
    </div>
    </div>
    """, unsafe_allow_html=True)

def login(email=None, password=None, is_demo=False):
    """Handle user login"""
    if email is None:
        email = st.session_state.get('login_email', '')
    if password is None:
        password = st.session_state.get('login_password', '')
        
    # Add debugging information
    st.write(f"Debug - Email value: '{email}', Password length: {len(password) if password else 0}")
    
    if not email or not password:
        st.error(f"Please enter both email and password. Email provided: {'Yes' if email else 'No'}, Password provided: {'Yes' if password else 'No'}")
        return
    
    try:
        with st.spinner("Logging in..."):
            if is_demo:
                # For demo, simulate successful login
                st.session_state.authenticated = True
                st.session_state.user_id = "demo-user"
                st.session_state.user_email = email
                st.session_state.user_name = "Demo User"
                st.success("Demo login successful!")
                st.rerun()
            else:
                # For real login flow
                success, result = supabase.sign_in(email, password)
                
                if success:
                    user = result
                    st.session_state.authenticated = True
                    st.session_state.user_id = user["id"]
                    st.session_state.user_email = user["email"]
                    st.session_state.user_name = user.get("name", email.split('@')[0])
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error(f"Login failed: {result}")
                    # Add more detailed error information
                    st.write(f"Error details - Email: '{email}', Password provided: {'Yes' if password else 'No'}")
    except Exception as e:
        st.error(f"Login failed: {str(e)}")
        # Show more information about the exception
        import traceback
        st.write(f"Exception details: {traceback.format_exc()}")

def signup():
    """Handle user registration"""
    email = st.session_state.signup_email
    password = st.session_state.signup_password
    password_confirm = st.session_state.signup_password_confirm
    name = st.session_state.get("signup_name", "")
    
    if not email or not password or not password_confirm:
        st.error("Please fill in all fields")
        return
        
    if not is_valid_email(email):
        st.error("Please enter a valid email address")
        return
        
    if password != password_confirm:
        st.error("Passwords do not match")
        return
        
    if len(password) < 6:
        st.error("Password must be at least 6 characters long")
        return
        
    try:
        with st.spinner("Creating account..."):
            success, result = supabase.sign_up(email, password, metadata={"name": name})
            
            if success:
                st.success("Account created successfully! Please check your email for verification.")
                # Auto-login for demo purposes
                st.session_state.login_email = email
                st.session_state.login_password = password
                login(is_demo=True)
            else:
                st.error(f"Registration failed: {result}")
    except Exception as e:
        st.error(f"Registration failed: {str(e)}")

def logout():
    """Handle user logout"""
    try:
        success = supabase.sign_out()
        if success:
            st.session_state.authenticated = False
            st.session_state.user_id = None
            st.session_state.user_email = None
            st.session_state.user_name = None
            st.success("You have been logged out")
            st.rerun()
        else:
            st.error("Logout failed")
    except Exception as e:
        st.error(f"Logout failed: {str(e)}") 