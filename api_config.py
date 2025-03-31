import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Firebase Authentication
FIREBASE_API_KEY = os.getenv("FIREBASE_API_KEY")
FIREBASE_AUTH_DOMAIN = os.getenv("FIREBASE_AUTH_DOMAIN")
FIREBASE_PROJECT_ID = os.getenv("FIREBASE_PROJECT_ID")

# Amazon S3
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")
AWS_BUCKET_NAME = os.getenv("AWS_BUCKET_NAME")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")

# SmallPDF API
SMALLPDF_API_KEY = os.getenv("SMALLPDF_API_KEY")
SMALLPDF_API_SECRET = os.getenv("SMALLPDF_API_SECRET")

# Google Cloud APIs
GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
GOOGLE_CLOUD_PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT_ID")

# Hugging Face
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
HUGGINGFACE_RESUME_SCORING_MODEL = os.getenv("HUGGINGFACE_RESUME_SCORING_MODEL", "resume-scoring/model")
HUGGINGFACE_RESUME_MATCHING_MODEL = os.getenv("HUGGINGFACE_RESUME_MATCHING_MODEL", "resume-matching/model")

# LanguageTool API
LANGUAGE_TOOL_HOST = os.getenv("LANGUAGE_TOOL_HOST", "https://api.languagetool.org")
LANGUAGE_TOOL_API_KEY = os.getenv("LANGUAGE_TOOL_API_KEY")

# Pusher
PUSHER_APP_ID = os.getenv("PUSHER_APP_ID")
PUSHER_APP_KEY = os.getenv("PUSHER_APP_KEY")
PUSHER_APP_SECRET = os.getenv("PUSHER_APP_SECRET")
PUSHER_CLUSTER = os.getenv("PUSHER_CLUSTER", "us2")

# PDFCrowd API
PDFCROWD_USERNAME = os.getenv("PDFCROWD_USERNAME")
PDFCROWD_API_KEY = os.getenv("PDFCROWD_API_KEY")

# Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Debug mode - set to True to enable detailed logging
DEBUG_MODE = True

# API Configuration Dictionary
API_CONFIG = {
    "firebase": {
        "api_key": FIREBASE_API_KEY,
        "auth_domain": FIREBASE_AUTH_DOMAIN,
        "project_id": FIREBASE_PROJECT_ID,
    },
    "aws_s3": {
        "access_key": AWS_ACCESS_KEY,
        "secret_key": AWS_SECRET_KEY,
        "bucket_name": AWS_BUCKET_NAME,
        "region": AWS_REGION,
    },
    "smallpdf": {
        "api_key": SMALLPDF_API_KEY,
        "api_secret": SMALLPDF_API_SECRET,
    },
    "google_cloud": {
        "credentials_path": GOOGLE_APPLICATION_CREDENTIALS,
        "project_id": GOOGLE_CLOUD_PROJECT_ID,
        "gemini_api_key": "AIzaSyDh281RCM63W2ir_QJmr_EKEgdCPyajaO0",
    },
    "huggingface": {
        "api_key": HUGGINGFACE_API_KEY,
        "resume_scoring_model": HUGGINGFACE_RESUME_SCORING_MODEL,
        "resume_matching_model": HUGGINGFACE_RESUME_MATCHING_MODEL,
    },
    "language_tool": {
        "host": LANGUAGE_TOOL_HOST,
        "api_key": LANGUAGE_TOOL_API_KEY,
    },
    "pusher": {
        "app_id": PUSHER_APP_ID,
        "app_key": PUSHER_APP_KEY,
        "app_secret": PUSHER_APP_SECRET,
        "cluster": PUSHER_CLUSTER,
    },
    "pdfcrowd": {
        "username": PDFCROWD_USERNAME,
        "api_key": PDFCROWD_API_KEY,
    },
    "supabase": {
        "url": SUPABASE_URL,
        "key": SUPABASE_KEY,
    },
    "openai": {
        "api_key": "your-openai-api-key"  # Replace with your OpenAI API key if using
    }
}

# Gemini API key for direct access
GEMINI_API_KEY = "AIzaSyDh281RCM63W2ir_QJmr_EKEgdCPyajaO0" 