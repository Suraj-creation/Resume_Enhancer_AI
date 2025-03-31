import os
from utils.supabase_client import initialize_supabase

def initialize_database():
    """Initialize database connection using Supabase client"""
    return initialize_supabase()

def save_resume_data(db, user_id, resume_data):
    """Save resume data to database"""
    try:
        # Insert resume data into resumes table
        response = db.table('resumes').insert({
            'user_id': user_id,
            'resume_data': resume_data,
            'created_at': 'now()'
        }).execute()
        
        # Return the inserted record ID
        if response.data and len(response.data) > 0:
            return response.data[0]['id']
        return None
    except Exception as e:
        print(f"Error saving resume data: {e}")
        return None

def get_user_resumes(db, user_id):
    """Get all resumes for a user"""
    try:
        response = db.table('resumes').select('*').eq('user_id', user_id).order('created_at', desc=True).execute()
        return response.data
    except Exception as e:
        print(f"Error retrieving user resumes: {e}")
        return []

def get_resume_by_id(db, resume_id):
    """Get a specific resume by ID"""
    try:
        response = db.table('resumes').select('*').eq('id', resume_id).execute()
        if response.data and len(response.data) > 0:
            return response.data[0]
        return None
    except Exception as e:
        print(f"Error retrieving resume: {e}")
        return None

def update_resume_data(db, resume_id, updated_data):
    """Update resume data"""
    try:
        response = db.table('resumes').update({
            'resume_data': updated_data,
            'updated_at': 'now()'
        }).eq('id', resume_id).execute()
        
        if response.data and len(response.data) > 0:
            return True
        return False
    except Exception as e:
        print(f"Error updating resume: {e}")
        return False

def delete_resume(db, resume_id):
    """Delete a resume"""
    try:
        response = db.table('resumes').delete().eq('id', resume_id).execute()
        return True
    except Exception as e:
        print(f"Error deleting resume: {e}")
        return False

def save_resume_enhancement(db, resume_id, enhanced_data, score):
    """Save enhanced resume version"""
    try:
        # Insert enhanced resume data
        response = db.table('resume_enhancements').insert({
            'resume_id': resume_id,
            'enhanced_data': enhanced_data,
            'score': score,
            'created_at': 'now()'
        }).execute()
        
        if response.data and len(response.data) > 0:
            return response.data[0]['id']
        return None
    except Exception as e:
        print(f"Error saving resume enhancement: {e}")
        return None

def get_resume_enhancements(db, resume_id):
    """Get all enhancements for a resume"""
    try:
        response = db.table('resume_enhancements').select('*').eq('resume_id', resume_id).order('created_at', desc=True).execute()
        return response.data
    except Exception as e:
        print(f"Error retrieving resume enhancements: {e}")
        return [] 