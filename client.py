import os
from supabase import create_client
from dotenv import load_dotenv

# Load environment variables once at startup
load_dotenv(r'c:\Users\user\OneDrive\Desktop\AI_Assignment\.env')

# Initialize Supabase client (already correct)
client = create_client(
    os.environ['SUPABASE_URL'],
    os.environ['SUPABASE_KEY']
)

# Gemini configuration (if needed)
GEMINI_CONFIG = {
    "api_key": os.environ['GEMINI_API_KEY'],
    "endpoint": "https://generativelanguage.googleapis.com/v1beta/models"
}