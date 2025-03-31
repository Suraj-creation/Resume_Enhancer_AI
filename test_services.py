#!/usr/bin/env python
"""Test script for AI services"""

import sys
import os
import traceback

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("Testing AI services...")

try:
    # Import necessary modules
    print("Importing modules...")
    from utils.ai_services.service_manager import AIServiceManager
    from utils.api_config import API_CONFIG, GEMINI_API_KEY
    
    # Check API key configuration
    print(f"Gemini API key in config: {'Yes' if API_CONFIG.get('google_cloud', {}).get('gemini_api_key') else 'No'}")
    print(f"Direct Gemini API key: {'Yes' if GEMINI_API_KEY else 'No'}")
    
    # Initialize service manager
    print("Initializing service manager...")
    manager = AIServiceManager()
    print("Service manager initialized successfully")
    
    # Get available services
    available_services = manager.get_available_services()
    print(f"Available services: {available_services}")
    
    # Test Gemini service
    print("Testing Gemini service...")
    gemini = manager.get_service('gemini')
    
    if gemini:
        print("Gemini service initialized successfully")
        
        # Generate text with Gemini
        print("Generating text with Gemini...")
        response = gemini.generate_text("Write a one-sentence test response.")
        print(f"Gemini response: {response}")
    else:
        print("Gemini service not available")
        
except Exception as e:
    print(f"Error: {str(e)}")
    print("Traceback:")
    traceback.print_exc()

print("Testing complete") 