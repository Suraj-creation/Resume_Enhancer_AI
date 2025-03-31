from src.api.client import client  # Supabase client
from src.api.client import GEMINI_CONFIG  # Gemini settings

# Example usage in another file
async def upload_to_supabase(file_data):
    response = client.storage.from_('resumes').upload(
        file=file_data,
        path='user_uploads/'
    )
    return response