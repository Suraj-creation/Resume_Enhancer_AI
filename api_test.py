"""Page for testing API connections and integrations."""

import streamlit as st

from utils.api_test import test_gemini_api
from utils.api_config import API_CONFIG, GEMINI_API_KEY
from utils.debug_utils import debug_log

def main():
    """Main function for the API test page."""
    st.set_page_config(page_title="API Testing", page_icon="🧪")
    
    st.title("🧪 API Connection Testing")
    st.write("Use this page to test various API connections and integrations.")
    
    # Create tabs for different tests
    tabs = st.tabs(["Gemini API", "Configuration", "About"])
    
    # Gemini API testing tab
    with tabs[0]:
        test_gemini_api()
        
        st.markdown("---")
        
        # Manual input for testing
        st.subheader("Manual Testing")
        test_prompt = st.text_area(
            "Enter a test prompt:", 
            "Write a one-sentence introduction for a software engineer with 5 years of experience.",
            height=100
        )
        
        if st.button("Run Custom Prompt"):
            with st.spinner("Generating response..."):
                try:
                    from utils.ai_services.service_manager import AIServiceManager
                    service_manager = AIServiceManager()
                    gemini_service = service_manager.get_service("gemini")
                    
                    if gemini_service:
                        response = gemini_service.generate_text(test_prompt)
                        st.markdown("### Response:")
                        st.success(response)
                    else:
                        st.error("Gemini service not available. Check your API key configuration.")
                except Exception as e:
                    st.error(f"Error generating response: {str(e)}")
                    debug_log(f"Error in manual prompt test: {str(e)}", level="ERROR")
    
    # Configuration tab
    with tabs[1]:
        st.subheader("Current Configuration")
        
        # Gemini API key info
        st.write("### Gemini API")
        if GEMINI_API_KEY:
            masked_key = f"{GEMINI_API_KEY[:5]}...{GEMINI_API_KEY[-3:]}" if len(GEMINI_API_KEY) > 8 else "***"
            st.code(f"GEMINI_API_KEY: {masked_key}")
        else:
            st.warning("GEMINI_API_KEY is not set")
        
        # API_CONFIG info
        st.write("### API_CONFIG")
        
        if "google_cloud" in API_CONFIG:
            st.write("Google Cloud Configuration:")
            for key, value in API_CONFIG["google_cloud"].items():
                if key == "gemini_api_key" and value:
                    masked_value = f"{value[:5]}...{value[-3:]}" if len(value) > 8 else "***"
                    st.code(f"{key}: {masked_value}")
                else:
                    st.code(f"{key}: {value}")
        else:
            st.warning("Google Cloud configuration not found in API_CONFIG")
        
        # Testing environment variables
        st.write("### Environment Variables")
        import os
        
        env_vars = [
            "GEMINI_API_KEY",
            "GOOGLE_APPLICATION_CREDENTIALS",
            "GOOGLE_CLOUD_PROJECT_ID"
        ]
        
        for var in env_vars:
            value = os.getenv(var)
            if value:
                if "API_KEY" in var:
                    masked_value = f"{value[:5]}...{value[-3:]}" if len(value) > 8 else "***"
                    st.code(f"{var}: {masked_value}")
                else:
                    st.code(f"{var}: {value}")
            else:
                st.code(f"{var}: Not set")
    
    # About tab
    with tabs[2]:
        st.subheader("About this Tool")
        st.write("""
        This page helps you test and troubleshoot API connections for the resume enhancer application.
        
        If you're having issues with the Gemini integration:
        
        1. Check that your API key is correctly configured
        2. Test the connection using the test buttons
        3. Try running a custom prompt to see if the API is responsive
        4. Check the logs folder for detailed error messages
        
        The application uses Gemini API for generating personalized feedback and improvements for resumes.
        """)

if __name__ == "__main__":
    main() 